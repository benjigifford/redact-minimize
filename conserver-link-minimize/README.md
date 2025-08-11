# Conserver Link Minimize

A vCon link for processing and minimizing Conserver conversation metadata using OpenAI's GPT models.

See documentation in conserver-link-redact for structure; this plugin drops non-essential fields.

## Example Config
```yaml
minimize:
  module: conserver-link-minimize
  options:
    minimization_model: "gpt-4o-mini"
    minimization_config:
      dialog:
        - fields_to_minimize: ["body"]
      analysis:
        - fields_to_minimize: ["body"]
```
