from pyresparser import ResumeParser
# data = ResumeParser('C:/Users/bmithran/Desktop/testres.pdf').get_extracted_data()
# print(data)
from flask import Flask, request, render_template
import pickle
from werkzeug.utils import secure_filename


def extractskillsall():
    mypath = 'C:/Users/bmithran/Desktop/resumes'
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir(mypath)]
    dict = {}
    for count, i in enumerate(onlyfiles):
        path = mypath + '/' + i
        print(path)
        from pyresparser import ResumeParser
        data = ResumeParser(path).get_extracted_data()
        print(data.get('skills'))
        dict[count] = data
    import pickle
    with open('master_skills_json.pkl', 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print(dict)


def getmatches(skills):
    with open('master_skills_json.pkl', 'rb') as handle:
        skills_master = pickle.load(handle)
    commondict = {}
    for i in skills_master:
        print(skills_master[i]['skills'])
        skilltemp = skills_master[i]['skills']
        commonskills = list(set(skilltemp).intersection(skills))
        if len(commonskills) > 0:
            commondict[skills_master[i]['name']] = commonskills
        # print(i['skills'])
    return commondict


app = Flask(__name__)


@app.route('/')
def my_form():
    extractskillsall()
    return render_template('index.html')


@app.route('/getpara')
def getpara():
    flag = False
    return render_template('getpara.html', flag=flag)


@app.route('/getpara', methods=['POST'])
def getpara_post():
    text = request.form['text']
    processed_text = text.lower()
    import aspose.words as aw
    # create document object
    doc = aw.Document()
    # create a document builder object
    builder = aw.DocumentBuilder(doc)
    # add text to the document
    builder.write(processed_text)
    # save document
    doc.save("out.docx")
    data = ResumeParser('C:/Users/bmithran/PycharmProjects/hiringhelp/out.docx').get_extracted_data()
    print(data['skills'])
    namedict = getmatches(data['skills'])
    data_skills = data['skills']
    while 'Apis' in data_skills: data_skills.remove('Apis')
    namedict = getmatches(data_skills)
    print(namedict)
    flag = True

    return render_template('getpara.html', namedict=namedict, flag=flag)


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename))
        data = ResumeParser('C:/Users/bmithran/PycharmProjects/hiringhelp/' + f.filename).get_extracted_data()
        interviewer_skills = data['skills']
        common = getmatches(interviewer_skills)

        return render_template('interviewer.html', flag=True, common=common)
    return render_template('interviewer.html', flag=False)


@app.route('/dashboard')
def dashboard():
    with open('master_skills_json.pkl', 'rb') as handle:
        skills_master = pickle.load(handle)
    print(skills_master)
    return render_template('dashboard.html', flag=True , skills_master=skills_master)


app.run()
