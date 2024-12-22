# Guide 
1. Add Azure OpenAI key into [.env](./docs/.env) file.
1. Update the [setting.yaml](./docs/settings.yaml) file with the right endpoints.
1. Run the following commands to create the index and query the markdown files.
1. Use the [prugraphrag.ipynb](./prugraphrag.ipynb) notebook to create markdown files based on the docs in the [original_files](./docs/original_files) directory.


## Create / update index of markdown files in a directory.
```bash
python3.10 -m graphrag.index --root ./docs
```

## Query using local method.
```bash
python3 -m graphrag.query \               
--root ./docs \
--method local \
"What is the campaign period for our reason is you contest?"
```

## Query using global method.
```bash
python3 -m graphrag.query \               
--root ./docs \ 
--method global \
"What are the top 5 themes in the data?"
```bash
