use phf::phf_map;
use rand::prelude::*;

extern crate pyo3;
use pyo3::prelude::*;


static CONSONANT: [char; 19] = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
static VOWEL: [char; 21] = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'];
static FINAL_CONSONANT: [char; 28] = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];
static DISTACH_EXCEPTIONS: [char; 12] = ['ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅗ'];
static LINKING_WORD: [char; 8] = ['이', '을', '를', '은', '았', '었', '아', '어'];

static CHANGE_VOWELS: phf::Map<char, char> = phf_map! {
    'ㅏ' => 'ㅑ', 'ㅑ' => 'ㅏ', 'ㅓ' => 'ㅕ', 'ㅕ' => 'ㅓ', 'ㅗ' => 'ㅛ', 'ㅛ' => 'ㅗ', 'ㅜ' => 'ㅠ', 'ㅠ' => 'ㅜ'
};

static PATALIZATION1: phf::Map<char, char> = phf_map! {'ㄷ'=>'ㅈ', 'ㅌ'=>'ㅊ'};
static PATALIZATION2: phf::Map<char, char> = phf_map! {'ㄷ'=>'ㅊ', 'ㄱ'=>'ㅋ'};

static LINKING: phf::Map<&str, &str> = phf_map! {
    "ㄻ"=>"ㄹㅁ", "ㅄ"=>"ㅂㅆ","ㄳ"=>"ㄱㅅ", "ㄽ"=>"ㄹㅅ", "ㅊ"=>" ㅊ", "ㅂ"=>" ㅂ", "ㅍ"=>" ㅂ", "ㄷ"=>" ㄹ", "ㄹ"=>" ㄹ", "ㄹㅎ"=>" ㄹ"
};

static LIQUIDIZATION: phf::Map<&str, &str> = phf_map! {"ㄴㄹ"=>"ㄹㄹ", "ㄹㄴ"=>"ㄹㄹ", "ㄾㄴ"=>"ㄹㄹ"};
static LIQUIDIZATION_EXPT: phf::Map<&str, &str> = phf_map! {"ㄴㄹㅕㄱ"=> "ㄴㄴ"};

static NASALIZATION: phf::Map<&str, &str> = phf_map! {"ㅂㅁ"=> "ㅁㅁ", "ㄷㄴ"=> "ㄴㄴ", "ㄱㅁ"=> "ㅇㅁ", "ㄱㄴ"=> "ㅇㄴ", "ㅇㄹ"=> "ㅇㄴ", "ㅁㄹ"=> "ㅁㄴ", "ㄲㄴ"=> "ㅇㄴ", "ㅂㄹ"=> "ㅁㄴ", "ㄱㄹ"=> "ㅇㄴ", "ㅊㄹ"=> "ㄴㄴ", "ㄺㄴ"=> "ㅇㄴ", "ㅍㄴ"=> "ㅁㄴ"};
static ASSIMILATION: phf::Map<&str, &str> = phf_map! {"ㄺㄴ"=> "ㅇㄴ"};


fn disassemble(ch:char) -> Vec<char>{
    let chn = ch as u32;
    if (chn < 44032)|(55203 < chn){
        return vec![ch, '\0', '\0'];
    }
    let base = ch as u32 - 44032;
    let c = base/588 ;
    let v = (base - 588 * c) / 28 ;
    let fc = base - 588 * c - 28 * v;

    vec![CONSONANT[c as usize], VOWEL[v as usize], FINAL_CONSONANT[fc as usize]]
}

fn assemble(jamolist:Vec<char>) -> char{
    if jamolist[1..] == ['\0', '\0'] {
        return jamolist[0]
    } else{
        let c = CONSONANT.iter().position(|&r| r ==jamolist[0]).unwrap();
        let v = VOWEL.iter().position(|&r| r ==jamolist[1]).unwrap();
        let fc = FINAL_CONSONANT.iter().position(|&r| r ==jamolist[2]).unwrap();
        return std::char::from_u32((fc + 588 * c + 28 * v + 44032) as u32).unwrap()
    }
}

fn disattach_letters(char_vec:Vec<char>)-> String{
    if char_vec[2] == ' ' && (!DISTACH_EXCEPTIONS.contains(&char_vec[1])){
        return char_vec.iter().collect::<String>().trim().to_string()
    }else {
        return assemble(char_vec).to_string()
    }
}

fn change_vowels(char_vec:Vec<char>) -> String {
    if char_vec[2] == ' ' && CHANGE_VOWELS.contains_key(&char_vec[1]){
        let changed = CHANGE_VOWELS.get(&char_vec[1]).unwrap().to_ascii_lowercase();
        return assemble(vec![char_vec[0], changed, char_vec[2]]).to_string();
    }else{
        return assemble(char_vec).to_string();
    }
}

fn patalization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    if PATALIZATION1.contains_key(&fc[2]) && nc[..2]==['ㅇ', 'ㅣ'] {
        let nnc = vec![PATALIZATION1.get(&fc[2]).unwrap().clone(),nc[1], nc[2]];
        let nfc = vec![fc[0], fc[1],' '];
        return (nfc, nnc)
    }else if PATALIZATION2.contains_key(&fc[2]) && (nc[0]=='ㅎ'){
        let nnc = vec![PATALIZATION2.get(&fc[2]).unwrap().clone(), nc[1], nc[2]];
        let nfc = vec![fc[0],fc[1],' '];
        return (nfc, nnc)
    }else{
        return (fc.clone(),nc.clone())
    }
}

fn linking(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    if LINKING.contains_key(&fc[2].to_string()) && LINKING_WORD.contains(&assemble(vec![nc[0],nc[1],nc[2]])){
        let v = LINKING.get(&fc[2].to_string()).unwrap().chars().collect::<Vec<char>>();
        let nfc = vec![fc[0],fc[1],v[0]];
        let nnc = vec![v[1], fc[1],fc[2]];
        return (nfc,nnc)
    }else{
        return (fc.clone(),nc.clone())
    }
}

fn liquidization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let key = fc[2].to_string();
    let (mut nfc, mut nnc) = (fc.clone(),nc.clone());
    if LIQUIDIZATION_EXPT.contains_key(&key){
        let v = LIQUIDIZATION_EXPT.get(&key.to_string()).unwrap().chars().collect::<Vec<char>>();
        nfc = vec![fc[0],fc[1], v[0]];
        nnc = vec![v[1], fc[1],fc[2]];
    }else if LIQUIDIZATION.contains_key(&[fc[2],nc[0]].iter().collect::<String>()){
        let v = LIQUIDIZATION_EXPT.get(&[fc[2],nc[0]].iter().collect::<String>()).unwrap().chars().collect::<Vec<char>>();
        nfc = vec![fc[0],fc[1],v[0]];
        nnc = vec![v[1],fc[1],fc[2]];
    }
    return (nfc, nnc)
}

fn nasalization(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let mut key = fc[2].to_string();
    key.push_str(&nc[0].to_string());
    let mut nfc = fc.clone();
    let mut nnc = nc.clone();
    if NASALIZATION.contains_key(&key) {
        let v = NASALIZATION.get(&key.to_string()).unwrap().chars().collect::<Vec<char>>();
        nfc = vec![fc[0],fc[1],v[0]];
        nnc = vec![v[1],nc[1],nc[2]];
    }
    (nfc, nnc)
}

fn assimilation(fc:&Vec<char>, nc:&Vec<char>) -> (Vec<char>, Vec<char>) {
    let mut key = fc[2].to_string();
    key.push_str(&nc[0].to_string());
    let mut nfc = fc.clone();
    let mut nnc = nc.clone();
    if ASSIMILATION.contains_key(&key) {
        let v = ASSIMILATION.get(&key.to_string()).unwrap().chars().collect::<Vec<char>>();
        nfc = vec![fc[0],fc[1],v[0]];
        nnc = vec![v[1],nc[1],nc[2]];
    }
    (nfc, nnc)
}


fn phonetic_change(text_vec:Vec<Vec<char>>, method:&str, prob:f64) -> Vec<Vec<char>> {
    let mut rng = rand::thread_rng();
    let mut mut_text = text_vec.clone();
    for i in 0..(mut_text.len()-1){
        let p: f64 = rng.gen();
        if p < prob {
            if method == "patalization" {
                let (v1, v2) = patalization(&mut_text[i], &mut_text[i + 1]);
                mut_text[i] = v1;
                mut_text[i + 1] = v2;
            } else if method == "linking" {
                let (v1, v2) = linking(&mut_text[i], &mut_text[i + 1]);
                mut_text[i] = v1;
                mut_text[i + 1] = v2;
            } else if method == "liquidization" {
                let (v1, v2) = liquidization(&mut_text[i], &mut_text[i + 1]);
                mut_text[i] = v1;
                mut_text[i + 1] = v2;
            } else if method == "nasalization" {
                let (v1, v2) = nasalization(&mut_text[i], &mut_text[i + 1]);
                mut_text[i] = v1;
                mut_text[i + 1] = v2;
            } else if method == "assimilation" {
                let (v1, v2) = assimilation(&mut_text[i], &mut_text[i + 1]);
                mut_text[i] = v1;
                mut_text[i + 1] = v2;
            }
        }
    }
    mut_text
}

#[pyfunction]
fn get_noise(_py: Python, text:&str, method:&str, prob:f64)-> PyResult<String>{
    let mut rng = rand::thread_rng();

    //dis-assembling
    let phonetics = ["palatalization","linking","liquidization","nasalization","assimilation"];
    let mut output = vec![];
    for ch in text.to_string().chars(){
        output.push(disassemble(ch));
    }
    let mut string_output = vec![];
    //adding the noise
    if method == "disattach-letters"{
        for out in output {
            let p: f64 = rng.gen();
            if p < prob{
                string_output.push(disattach_letters(out));
            }else {
                string_output.push(assemble(out).to_string());
            }
        }
    }else if method == "change-vowels"{
        for out in output {
            let p: f64 = rng.gen();
            if p < prob {
                string_output.push(change_vowels(out));
            }else {
                string_output.push(assemble(out).to_string());
            }
        }
    }else if phonetics.contains(&method){
        let mut_output = phonetic_change(output, &method, prob);
        for out in mut_output {
            string_output.push(assemble(out).to_string());
        }
    }else {
         for out in output {
            string_output.push(assemble(out).to_string());
         }
    }
    //assembling
    Ok(string_output.join(""))
}


#[pymodule]
fn noise_generate(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_noise, m)?)?;

    Ok(())
}