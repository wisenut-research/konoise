import timeit
from konoise import NoiseGenerator
from datasets import load_dataset
DOWNLOAD = "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"
dataset = load_dataset("psyche/daangn", use_auth_token=DOWNLOAD, streaming=True)
texts = [d["content"] for d in dataset['train'].take(100)]
generator = NoiseGenerator()
print(timeit.timeit(lambda : generator.batch_generate(texts,use_rust_tokenizer=True), number=1))
print(timeit.timeit(lambda : generator.batch_generate(texts,use_rust_tokenizer=False), number=1))
