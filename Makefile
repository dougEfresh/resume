export:
	python resume.py

deploy: export
	scp resume.html resume.dougchimento.com:/var/lib/nginx/resume/index.html
	scp resume.pdf resume.dougchimento.com:/var/lib/nginx/resume/resume.pdf
