export:
	python resume.py

deploy: export
	 aws --profile resume s3 cp resume.html s3://resume-douglaschimento/index.html
	 aws --profile resume s3 cp error.html s3://resume-douglaschimento/error.html
	 aws --profile resume s3 cp resume.pdf s3://resume-douglaschimento/resume.pdf
