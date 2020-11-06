from flask import Flask,url_for,render_template,request,send_file,redirect
from flask import  current_app, flash, jsonify, make_response, redirect, request, url_for
from flask_uploads import UploadSet,configure_uploads,ALL,DATA,TEXT, DOCUMENTS
from werkzeug.utils import secure_filename
from io import StringIO
import textract

# Other Packages
import os
import spacy
#nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("xx_ent_wiki_sm")

import time
timestr = time.strftime("%Y%m%d-%H%M%S")

# Initialize App
app = Flask(__name__)
# Configuration For Uploads - Here experimented with textract, but didnt manage to upload other than txt
files = UploadSet('files',DATA + TEXT + DOCUMENTS)
app.config['UPLOADED_FILES_DEST'] = 'static/uploadedfiles'
configure_uploads(app,files)



def cleanf(rawtext):
	result5 = sanitize_date(rawtext)
	result4 = sanitize_names(result5)
	result3 = sanitize_places(result4)
	result2 = sanitize_org(result3)
	result1 = sanitize_names(result2)
	result = str(result1)


	return result
# Functions to Sanitize and Redact 
def sanitize_names(text):
	nm = request.form['name']
	if nm != "":
		docx = nlp(text)
		redacted_sentences = []
		for ent in docx.ents:
			ent.merge()
		for token in docx:
			if token.ent_type_ == 'PER':
				redacted_sentences.append(nm)
			else:
				redacted_sentences.append(token.string)
		return "".join(redacted_sentences)
	else:
		redacted_sentences = []
		redacted_sentences.append(text)
		return "".join(redacted_sentences)

def sanitize_places(text):
	plc = request.form['place']
	if plc != "":
		docx = nlp(text)
		redacted_sentences = []
		for ent in docx.ents:
			ent.merge()
		for token in docx:
			if token.ent_type_ == 'LOC':
				redacted_sentences.append(plc)
			else:
				redacted_sentences.append(token.string)
		return "".join(redacted_sentences)
	else:
		redacted_sentences = []
		redacted_sentences.append(text)
		return "".join(redacted_sentences)

def sanitize_date(text):
	misc = request.form['date']
	if misc != "":
		docx = nlp(text)
		redacted_sentences = []
		for ent in docx.ents:
			ent.merge()
		for token in docx:
			if token.ent_type_ == 'MISC':
				redacted_sentences.append(misc)
			else:
				redacted_sentences.append(token.string)
		return "".join(redacted_sentences)
	else:
		redacted_sentences = []
		redacted_sentences.append(text)
		return "".join(redacted_sentences)

def sanitize_org(text):
	orgz = request.form['organisation']
	if orgz != "":
		docx = nlp(text)
		redacted_sentences = []
		for ent in docx.ents:
			ent.merge()
		for token in docx:
			if token.ent_type_ == 'ORG':
				redacted_sentences.append(orgz)
			else:
				redacted_sentences.append(token.string)
		return "".join(redacted_sentences)
	else:
		redacted_sentences = []
		redacted_sentences.append(text)
		return "".join(redacted_sentences)
#For the above we can enter in the same way other tags (F.ex Currency etc.)


def writetofile(text):
	file_name = 'yourdocument' + timestr + '.txt'
	with open(os.path.join('static/downloadfiles',file_name),'w') as f:
		f.write(text)
#Here we should change the path for cloud;

		
@app.route('/')
def index():
	return render_template('text.html')


@app.route('/document')
def document():
	return render_template('document.html')


@app.route('/text', methods=["GET"])
def text():
    return render_template('text.html')



@app.route('/sanitize',methods=['GET','POST'])
def sanitize():
	if request.method == 'POST':
		misc =  request.form['date']
		plc = request.form['place']
		orgz = request.form['organisation']
		nm = request.form['name']
		rawtext = request.form['text']
		result5 = sanitize_date(rawtext)
		result4 = sanitize_names(result5)
		result3 = sanitize_places(result4)
		result2 = sanitize_org(result3)
		result1 = sanitize_names(result2)
		result = str(result1)
		return  jsonify({"output":result})


@app.route('/uploads',methods=['GET','POST'])
def uploads():
	if request.method == 'POST':
		misc =  request.form['date']
		plc = request.form['place']
		orgz = request.form['organisation']
		nm = request.form['name']
		file = request.files['file']
		#choice = request.form['saveoption']
		filename = secure_filename(file.filename)
		file.save(os.path.join('static/uploadedfiles',filename))
		# Document Redaction Here
		with open(os.path.join('static/uploadedfiles',filename),'r+') as f:
			myfile = textract.process(os.path.join('static/uploadedfiles',filename)).decode('utf-8')
			rawtext= str(myfile)
			result = cleanf(rawtext)
		return  jsonify({"output":result})






#if choice == 'savetotxt':
#			new_res = writetofile(result)
#			return redirect(url_for('downloads'))
#		elif choice == 'savetodocx':
#			new_res_docx = writetofile(result)
#			return redirect(url_for('downloads'))
#		elif choice == 'savetoxlsx':
#			new_res_xlsx = writetofile(result)
#			return redirect(url_for('downloads'))
#		elif choice == 'savetoppt':
#			new_res_ppt = writetofile(result)
#			return redirect(url_for('downloads' ))
#		elif choice == 'no_save':
#			pass
#		else:
#			pass


@app.route('/downloads')
def downloads():
	files = os.listdir(os.path.join('static/downloadfiles'))
	return render_template('downloadsdirectory.html',files=files)

if __name__ == '__main__':
	app.run(debug=True)
