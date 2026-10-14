# Zero-shot user prompt template

Built by `api_prompts.build_zero_shot_user_prompt(instruction)`:

```
Write the instruction file described below.

{strip_task_prefix(instruction)}

Instruction file:
```

`instruction` is the pair `input` field (repo summary + requested categories).
The helper strips a leading `generate agent instructions: ` prefix when present.
