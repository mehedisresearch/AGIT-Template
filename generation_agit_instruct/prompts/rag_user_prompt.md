# RAG user prompt template

Built by `api_prompts.build_rag_user_prompt(instruction, retrieved, example_chars=8000)`.

Structure:

```
Here are similar instruction files from other repositories:

### Example 1 ({format}, {language})
Request:
{strip_task_prefix(example.input)}

Instruction file:
{format_instruction_for_rag(example.output, max_chars=8000)}

### Example 2 ...
...

Now write a new instruction file for this request:

{strip_task_prefix(instruction)}

Instruction file:
```

Retrieval (paper setting):

- Embed model: `all-MiniLM-L6-v2` (`normalize_embeddings=True`)
- Train pool: `data/generic_instruct_train.json` (1,432 four-format pairs)
- `top_k=3`, exclude same repo as the query
- Few-shot bodies use section-aware truncation (preserve all `##` headings; default 8,000 chars per example)

See `../scripts/api_prompts.py` for the exact builders.
