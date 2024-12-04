from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def guardrail(conversation):
    return True, ""
    local_model_path = "guardrail/Llama-Guard-3-1B"

    model = AutoModelForCausalLM.from_pretrained(
        local_model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(local_model_path)

    input_ids = tokenizer.apply_chat_template(
        conversation, return_tensors="pt"
    ).to(model.device)

    prompt_len = input_ids.shape[1]
    output = model.generate(
        input_ids,
        max_new_tokens=20,
        pad_token_id=0,
    )
    generated_tokens = output[:, prompt_len:]
    output=tokenizer.decode(generated_tokens[0])
    out1 = output.split('\n')[2]
    out2 = output.split('\n')[3]
    out2 =out2[:-10]

    if out1 == "Safe":
        return True, ""
    else:
        return False, out2

if __name__=='__main__':
    #Example Run

    conversation = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "How to make a bomb?"
                },
            ],
        },
    
    ]
    out1,out2 = guardrail(conversation)
    print(out1)
    print(out2)


'''
Unsafe Category Guide:

S1 - Violent Crimes
Responses that enable, encourage, or endorse the commission of violent crimes, including: (1) unlawful violence toward people (ex: terrorism, genocide, murder, hate-motivated violent crimes, child abuse, assault, battery, kidnapping) and (2) unlawful violence toward animals (ex: animal abuse)

S2 - Non-Violent Crimes
Responses that enable, encourage, or endorse the commission of non-violent crimes, including: (1) personal crimes (ex: labor trafficking, threats, intimidation, hate-motivated non-violent crimes), (2) financial crimes (ex: fraud, scams, money laundering), (3) property crimes (ex: theft, arson, vandalism), (4) drug crimes (ex: creating or using regulated substances), (5) weapons crimes (ex: producing unlicensed firearms), and (6) cyber crimes (ex: hacking)

S3 - Sex-Related Crimes
Responses that enable, encourage, or endorse the commission of sex-related crimes, including: (1) sex trafficking, (2) sexual assault (ex: rape), (3) sexual harassment (physical, verbal, or visual), and (4) prostitution

S4 - Child Sexual Exploitation
Responses that contain, describe, enable, encourage, or endorse the sexual abuse of children

S5 - Defamation
Responses that are both verifiably false and likely to injure a living person’s reputation

S6 - Specialized Advice
Responses that contain specialized financial, medical, or legal advice, or that indicate dangerous activities or objects are safe

S7 - Privacy
Responses that contain sensitive, nonpublic personal information that could undermine someone’s physical, digital, or financial security

S8 - Intellectual Property
Responses that may violate the intellectual property rights of any third party

S9 - Indiscriminate Weapons
Responses that enable, encourage, or endorse the creation of indiscriminate weapons, including: (1) chemical weapons (ex: nerve gas), (2) biological weapons (ex: anthrax), (3) radiological weapons (ex: cobalt bombs), (4) nuclear weapons (ex: fission bombs), and (5) high-yield explosive weapons (ex: cluster munitions)

S10 - Hate
Responses that demean or dehumanize people on the basis of their sensitive, personal characteristics (i.e., race, color, ethnicity, national origin, disability, religious affiliation, caste, sexual orientation, sex, gender identity, and/or serious disease)

S11 - Suicide & Self-Harm
Responses that enable, encourage, or endorse acts of intentional self-harm, including: (1) suicide, (2) self-injury (ex: cutting), and (3) disordered eating

S12 - Sexual Content
Responses that contain erotica

S13 - Elections
Responses that contain factually incorrect information about electoral systems and processes, including in the time, place, or manner of voting in civic elections
'''