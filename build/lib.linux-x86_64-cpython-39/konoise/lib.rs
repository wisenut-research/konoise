use phf::phf_map;
use rand::prelude::*;
extern crate pyo3;
use pyo3::prelude::*;
use rayon::prelude::*;


static PHONETICS: [&str; 5] = ["palatalization","linking","liquidization","nasalization","assimilation"];

static CONSONANT: [char; 19] = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
static VOWEL: [char; 21] = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'];
static FINAL_CONSONANT: [char; 28] = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
static DISTACH_EXCEPTIONS: [char; 12] = ['ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅗ'];
static LINKING_WORD: [char; 8] = ['이', '을', '를', '은', '았', '었', '아', '어'];

static CHANGE_VOWELS: phf::Map<char, char> = phf_map! {'ㅏ' => 'ㅑ', 'ㅑ' => 'ㅏ', 'ㅓ' => 'ㅕ', 'ㅕ' => 'ㅓ', 'ㅗ' => 'ㅛ', 'ㅛ' => 'ㅗ', 'ㅜ' => 'ㅠ', 'ㅠ' => 'ㅜ'};

static PATALIZATION1: phf::Map<char, char> = phf_map! {'ㄷ'=>'ㅈ', 'ㅌ'=>'ㅊ'};
static PATALIZATION2: phf::Map<char, char> = phf_map! {'ㄷ'=>'ㅊ', 'ㄱ'=>'ㅋ'};

static LINKING: phf::Map<&str, &str> = phf_map! { "ㄻ"=>"ㄹㅁ", "ㅄ"=>"ㅂㅆ","ㄳ"=>"ㄱㅅ", "ㄽ"=>"ㄹㅅ", "ㅊ"=>" ㅊ", "ㅂ"=>" ㅂ", "ㅍ"=>" ㅂ", "ㄷ"=>" ㄹ", "ㄹ"=>" ㄹ", "ㄹㅎ"=>" ㄹ"};

static LIQUIDIZATION: phf::Map<&str, &str> = phf_map! {"ㄴㄹ"=>"ㄹㄹ", "ㄹㄴ"=>"ㄹㄹ", "ㄾㄴ"=>"ㄹㄹ"};
static LIQUIDIZATION_EXPT: phf::Map<&str, &str> = phf_map! {"ㄴㄹㅕㄱ"=> "ㄴㄴ"};

static NASALIZATION: phf::Map<&str, &str> = phf_map! {"ㅂㅁ"=> "ㅁㅁ", "ㄷㄴ"=> "ㄴㄴ", "ㄱㅁ"=> "ㅇㅁ", "ㄱㄴ"=> "ㅇㄴ", "ㅇㄹ"=> "ㅇㄴ", "ㅁㄹ"=> "ㅁㄴ", "ㄲㄴ"=> "ㅇㄴ", "ㅂㄹ"=> "ㅁㄴ", "ㄱㄹ"=> "ㅇㄴ", "ㅊㄹ"=> "ㄴㄴ", "ㄺㄴ"=> "ㅇㄴ", "ㅍㄴ"=> "ㅁㄴ"};
static ASSIMILATION: phf::Map<&str, &str> = phf_map! {"ㄺㄴ"=> "ㅇㄴ"};


fn disassemble(ch:char) -> Vec<char>{
    let chn = ch as u32;
    if (chn < 44032)|(55203 < chn){
        return vec![ch, '\0', '\0'];
    }
    let base = (ch as u32 - 44032) as usize;
    let c = base/588 ;
    let v = (base - 588 * c) / 28 ;
    let fc = base - 588 * c - 28 * v;

    vec![CONSONANT[c], VOWEL[v], FINAL_CONSONANT[fc]]
}


fn assemble(jamo_list: &Vec<char>) -> char{
    if jamo_list[1..] == ['\0', '\0'] {
        jamo_list[0]
    } else{

        let c = CONSONANT.iter().position(|&r| r == jamo_list[0]).unwrap();
        let v = VOWEL.iter().position(|&r| r == jamo_list[1]).unwrap();
        let fc = FINAL_CONSONANT.iter().position(|&r| r == jamo_list[2]).unwrap();
        std::char::from_u32((fc + 588 * c + 28 * v + 44032) as u32).unwrap()
    }
}


fn disattach_letters(char_vec: &Vec<char>) -> String{
    if char_vec[2] == ' ' && (!DISTACH_EXCEPTIONS.contains(&char_vec[1])){
        char_vec.iter().collect::<String>().trim().to_string()
    }else {
        assemble(char_vec).to_string()
    }
}

fn change_vowels(char_vec:&Vec<char>) -> String {
    if char_vec[2] == ' ' && CHANGE_VOWELS.contains_key(&char_vec[1]){
        let changed = CHANGE_VOWELS.get(&char_vec[1]).unwrap().to_ascii_lowercase();
        assemble(&vec![char_vec[0], changed, char_vec[2]]).to_string()
    }else{
        assemble(&char_vec).to_string()
    }
}


fn patalization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    if PATALIZATION1.contains_key(&fc[2]) && nc[..2]==['ㅇ', 'ㅣ'] {
        (vec![fc[0], fc[1],' '], vec![PATALIZATION1.get(&fc[2]).unwrap().clone(),nc[1], nc[2]])
    }else if PATALIZATION2.contains_key(&fc[2]) && (nc[0]=='ㅎ'){
        (vec![fc[0],fc[1],' '], vec![PATALIZATION2.get(&fc[2]).unwrap().clone(), nc[1], nc[2]])
    }else{
        (fc.clone(), nc.clone())
    }
}


fn linking(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    if LINKING.contains_key(&fc[2].to_string()) && LINKING_WORD.contains(&assemble(&vec![nc[0],nc[1],nc[2]])){
        let v = LINKING.get(&fc[2].to_string()).unwrap().chars().collect::<Vec<char>>();
        (vec![fc[0],fc[1],v[0]],vec![v[1], fc[1],fc[2]])
    }else{
        return (fc.clone(),nc.clone())
    }
}


fn liquidization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let key = fc[2].to_string();
    let (nfc, nnc) = (fc.clone(),nc.clone());
    if LIQUIDIZATION_EXPT.contains_key(&key){
        let v = LIQUIDIZATION_EXPT.get(&key.to_string()).unwrap().chars().collect::<Vec<char>>();
        (vec![fc[0],fc[1], v[0]], vec![v[1], fc[1],fc[2]])
    } else if LIQUIDIZATION.contains_key(&[fc[2],nc[0]].iter().collect::<String>()){
        let v = LIQUIDIZATION_EXPT.get(&[fc[2],nc[0]].iter().collect::<String>()).unwrap().chars().collect::<Vec<char>>();
        (vec![fc[0],fc[1],v[0]], vec![v[1],fc[1],fc[2]])
    } else {
        (nfc, nnc)
    }
}

fn nasalization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let mut key = fc[2].to_string();
    key.push_str(&nc[0].to_string());

    if NASALIZATION.contains_key(&key) {
        let v = NASALIZATION.get(&key).unwrap().chars().collect::<Vec<char>>();
        (vec![fc[0],fc[1],v[0]], vec![v[1],nc[1],nc[2]])
    }else{
        (fc.clone(), nc.clone())
    }

}

fn assimilation(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let mut key = fc[2].to_string();
    key.push_str(&nc[0].to_string());

    if ASSIMILATION.contains_key(&key) {
        let v = ASSIMILATION.get(&key).unwrap().chars().collect::<Vec<char>>();
        (vec![fc[0],fc[1],v[0]], vec![v[1],nc[1],nc[2]])
    }else{
        (fc.clone(), nc.clone())
    }
}


fn phonetic_change(text_vec:Vec<Vec<char>>, method:&str, prob:f64) -> Vec<Vec<char>> {
    let mut rng = rand::thread_rng();
    let mut mut_text = text_vec.clone();
    for i in 0..(mut_text.len()-1){
        let p: f64 = rng.gen();
        if p < prob {
            let func = match method{
                "patalization" => patalization,
                "liquidization" => liquidization,
                "nasalization" => nasalization,
                "assimilation" => assimilation,
                "linking" => linking,
                _ => panic!()
            };
            let (a, b) = func(&mut_text[i], &mut_text[i + 1]);
            mut_text[i] = a;
            mut_text[i + 1] = b;
        }
    }
    mut_text
}

fn get_noise_output(text:&str, method:&str, prob:f64) -> String{
    let mut rng = rand::thread_rng();
    let output = text.chars().map(|x| disassemble(x)).collect::<Vec<Vec<char>>>();

    match method {
        "disattach-letters" => output.iter().map(
            |x| match x {
                x if rng.gen::<f64>() < prob => disattach_letters(x),
                x => assemble(x).to_string()
            }).collect::<Vec<String>>(),

        "change-vowels" => output.iter().map(
            |x| match x {
                x if rng.gen::<f64>() < prob => change_vowels(x).to_string(),
                x => assemble(x).to_string()
            }).collect::<Vec<String>>(),

        _x if PHONETICS.contains(&method) => phonetic_change(output, &method, prob).iter().map(|x| assemble(x).to_string()).collect::<Vec<String>>(),

        _ => output.iter().map(|x| assemble(x).to_string()).collect::<Vec<String>>()
    }.iter().map(|x| x.to_string()).collect::<Vec<String>>().join("")
}

#[pyfunction]
fn get_noise(_py: Python, text:&str, method:&str, prob:f64)-> PyResult<String>{
    Ok(get_noise_output(text, method, prob))
}

#[pyfunction]
fn get_noise_batch(_py: Python, texts:Vec<&str>, method:&str, prob:f64)-> PyResult<Vec<String>>{
    Ok(texts.par_iter().map(|&x| get_noise_output(x, method, prob)).collect::<Vec<String>>())
}


#[pymodule]
fn rust_generator(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_noise, m)?)?;
    m.add_function(wrap_pyfunction!(get_noise_batch, m)?)?;
    Ok(())
}
