from transformers import AutoTokenizer, AutoModelForMaskedLM
from splade.models.transformer_rep import Splade
import torch


def splade(doc, model_id):
    model = AutoModelForMaskedLM.from_pretrained(sparse_model_id)
    tokenizer = AutoTokenizer.from_pretrained(sparse_model_id)
    tokens = tokenizer(doc, return_tensors="pt")
    output = model(**tokens)
    # output.logits
    vec = torch.max(
    torch.log(
        1 + torch.relu(output.logits)
    ) * tokens.attention_mask.unsqueeze(-1),
    dim=1)[0].squeeze()
    return vec

sparse_model_id = 'naver/splade-cocondenser-ensembledistil'
# With Naver's Splade model, we can get the sparse representation of a document
sparse_model = Splade(sparse_model_id, agg="max")

tokenizer = AutoTokenizer.from_pretrained(sparse_model_id)
model = AutoModelForMaskedLM.from_pretrained(sparse_model_id)


def splade_query_main(doc):
    tokens = tokenizer(doc, return_tensors="pt")
    output = model(**tokens)
    # output.logits
    vec = torch.max(
    torch.log(
        1 + torch.relu(output.logits)
    ) * tokens.attention_mask.unsqueeze(-1),
    dim=1)[0].squeeze()
    cols = torch.nonzero(vec).squeeze().cpu().tolist()
    weights = vec[cols].cpu().tolist()
    sparse_dict = dict(zip(cols, weights))
    # extract the ID position to text token mappings
    idx2token = {
        idx: token for token, idx in tokenizer.get_vocab().items()
    }
    # map token IDs to human-readable tokens
    sparse_dict_tokens = {
        idx2token[idx]: round(weight, 2) for idx, weight in zip(cols, weights)
    }
    # sort so we can see most relevant tokens first
    sparse_dict_tokens = {
        k: v for k, v in sorted(
            sparse_dict_tokens.items(),
            key=lambda item: item[1],
            reverse=True
        )
    }
    return sparse_dict_tokens


def splade_query(doc):
    tokens = tokenizer(doc, return_tensors="pt")
    with torch.no_grad():
        vec = sparse_model(d_kwargs=tokens)["d_rep"].squeeze()
    cols = torch.nonzero(vec).squeeze().cpu().tolist()
    weights = vec[cols].cpu().tolist()
    sparse_dict = dict(zip(cols, weights))
    # extract the ID position to text token mappings
    idx2token = {
        idx: token for token, idx in tokenizer.get_vocab().items()
    }
    # map token IDs to human-readable tokens
    sparse_dict_tokens = {
        idx2token[idx]: round(weight, 2) for idx, weight in zip(cols, weights)
    }
    # sort so we can see most relevant tokens first
    sparse_dict_tokens = {
        k: v for k, v in sorted(
            sparse_dict_tokens.items(),
            key=lambda item: item[1],
            reverse=True
        )
    }