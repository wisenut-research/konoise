import timeit
from konoise import NoiseGenerator
from datasets import load_dataset

DOWNLOAD = "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"
dataset = load_dataset("psyche/daangn", use_auth_token=DOWNLOAD, streaming=True)
texts = [d["content"] for d in dataset['train'].take(100)]
generator = NoiseGenerator()
print(timeit.timeit(lambda : [generator.generate(t, use_rust_tokenizer=False) for t in texts], number=1000))
print(timeit.timeit(lambda : [generator.generate(t, use_rust_tokenizer=True) for t in texts], number=1000))
print(timeit.timeit(lambda : generator.generate_b(texts), number=1000))