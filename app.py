from flask import Flask ,render_template,request,url_for,redirect,session,flash
from flask_mysqldb import MySQL
from datetime import datetime, timedelta


def paiment(nbr_seance,mode):   # mode = test ou permanent 
    if mode == 'test' : return 200
    return int(nbr_seance)*150


app=Flask(__name__)
app.secret_key = 'hicham_smati'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "anprojet"

mysql= MySQL(app)


@app.route('/',methods=['POST','GET'])
def home(): return render_template('index_home.html')

@app.route('/classe')
def classe(): return render_template('index_classe.html')

@app.route('/contact')
def contact(): return render_template('index_contact.html')



@app.route('/admin',methods=['POST','GET'])
def check():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cur=mysql.connection.cursor()
        cur.execute("SELECT * FROM admin_c ")
        result = cur.fetchall()  
        cur.close()
        list_admin=[(x[1],x[2]) for x in result ]
        if (email,password)  in list_admin:
            return redirect(url_for('student'))
        else:
            return render_template('loginpage.html',message='information non valide ressayer')
    return render_template('loginpage.html')

@app.route('/student',methods=['POST','GET'])
def student():
    return render_template('index_student.html')

@app.route('/professeur')
def professeur():
    return render_template('index_prof.html')

@app.route('/groups')
def groups():
    return render_template('index_groups.html')

@app.route('/seance')
def seance():
    return render_template('index_seance.html')

@app.route('/utilisateur')
def utilisateur():
    return render_template('index_admin.html')

@app.route('/addstudent', methods=['GET', 'POST'])
def addstudent():
    if request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        tel = request.form['telephone']
        email = request.form['email']
        formation=request.form['formation']  # language  / softSkills / schoolSupport 
        mode=request.form['mod']
        if mode =='test':
            nbr_seance=1
            pay=paiment(nbr_seance,mode)
        else :
            nbr_seance=request.form['nbrSeance1']
            pay=paiment(nbr_seance,mode)
        if formation == 'language' : 
            language = request.form['languageSelect'] # french / english / spanish 
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO eleve(nomEleve, prenomEleve,emailEleve, tel,paiement) VALUES (%s, %s, %s, %s,%s)",(lastName, firstName,  email, tel,pay))
            mysql.connection.commit()
            cur.execute("SELECT MAX(idElv) FROM eleve;")
            id_el=cur.fetchall()[0] 
            print(id_el)
            cur.execute("SELECT *  from langue where nomLangue = (%s)",(language,))
            id_langue=cur.fetchall()[0][0]
            print(id_langue)
            cur.execute("INSERT INTO absences_l (idElv,idLangue,nbr_séances,nbr_séances_restantes,nbr_séances_abscentes) VALUES (%s,%s,%s,%s,%s)",(id_el,id_langue,nbr_seance,nbr_seance,0))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('integrer', formation=language,id_el=id_el))

        elif formation =='schoolSupport' :     
            niveau = request.form['schoolLevelSelect']
            matiere = request.form['schoolSubjectSelect']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO eleve(nomEleve, prenomEleve,niveauScolaire,emailEleve, tel,paiement) VALUES (%s, %s, %s, %s,%s,%s)",(lastName, firstName,niveau,  email, tel,pay,))
            mysql.connection.commit()
            cur.execute("SELECT MAX(idElv) FROM eleve;")
            id_el=cur.fetchall()[0]
            print(id_el)
            cur.execute("SELECT *  from matiere where nomMatiere = (%s)",(matiere,))
            id_matiere=cur.fetchall()[0][0]
            print(id_matiere)
            cur.execute("INSERT INTO absences_m (idElv,idMatiere,nbr_séances,nbr_séances_restantes,nbr_séances_abscentes) VALUES (%s,%s,%s,%s,%s)",(id_el,id_matiere,nbr_seance,nbr_seance,0))
            mysql.connection.commit()
            cur.close()   
            return redirect(url_for('integrer', niveau=niveau, formation=matiere,id_el=id_el))
           
        else :
            skill = request.form['SkillsSelect']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO eleve(nomEleve, prenomEleve,emailEleve, tel,paiement) VALUES ( %s, %s, %s,%s,%s)",(lastName, firstName,  email, tel,pay,))
            mysql.connection.commit()
            cur.execute("SELECT MAX(idElv) FROM eleve;")
            id_el=cur.fetchall()[0]
            print(id_el)
            cur.execute("SELECT *  from skills where nomSkills = (%s)",(skill,))
            id_skill=cur.fetchall()[0][0]
            print(id_skill)
            cur.execute("INSERT INTO absences_s (idElv,idSkills,nbr_séances,nbr_séances_restantes,nbr_séances_abscentes) VALUES (%s,%s,%s,%s,%s)",(id_el,id_skill,nbr_seance,nbr_seance,0))
            mysql.connection.commit()
            cur.close()                   
            return redirect(url_for('integrer', formation=skill,id_el=id_el))
    return render_template('addstudent.html')

@app.route('/integrer',methods=['GET', 'POST'])
def integrer():
    id_el = request.args.get('id_el')
    niveau = request.args.get('niveau')
    formation = request.args.get('formation')
    if request.method=='POST':
        cur = mysql.connection.cursor()
        id_groupe =request.form['Id']
        cur.execute("insert into  integrer (idElv,idGrp) values(%s,%s)",(id_el,id_groupe,))
        mysql.connection.commit()
        cur.execute("update groupe set nbr_eleve =nbr_eleve +1  where idGrp=%s;",(id_groupe,))
        mysql.connection.commit()
        return redirect(url_for('student'))   
    if niveau!=None:
        cur = mysql.connection.cursor()
        cur.execute("select  * from groupe  where niveauScolaire =%s and formation =%s and nbr_eleve < 8 ",(niveau,formation,))
        groups=cur.fetchall()
        if not groups:
            cur.execute('''SELECT MAX(numGrp) FROM Groupe WHERE formation = %s and niveauScolaire=%s;''', (formation, niveau,))
            max_num = cur.fetchone()
            if max_num[0] is None:
                max_num = (0,)
            cur.execute("insert into groupe (numGrp,niveauScolaire,formation,nbr_eleve) values (%s,%s,%s,%s)", (int(max_num[0])+1, niveau, formation,0))
            mysql.connection.commit()
            cur.execute("select  * from groupe  where niveauScolaire =%s and formation =%s and nbr_eleve < 8 ",(niveau,formation,))
            groups=cur.fetchall()
    else:
        cur = mysql.connection.cursor()
        cur.execute("select  * from groupe  where  formation =%s and nbr_eleve < 8 ",(formation,))
        groups=cur.fetchall()
        if not groups:
            cur.execute('''SELECT MAX(numGrp) FROM Groupe WHERE formation = %s ;''', (formation,))
            max_num = cur.fetchone()
            if max_num[0] is None:
                max_num = (0,)
            cur.execute("insert into groupe (numGrp,formation,nbr_eleve) values (%s,%s,%s)", (int(max_num[0])+1,formation,0))
            mysql.connection.commit()
            cur.execute("select  * from groupe  where  formation =%s and nbr_eleve < 8 ",(formation,))
            groups=cur.fetchall()
    return render_template('integrer.html',groups=groups)

@app.route('/addprof',methods=['GET', 'POST'])
def addprof():
    if request.method=='POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        tel = request.form['telephone']
        email = request.form['email']
        formation=request.form['formation']  
        if formation=='schoolSupport':      
            matiere=request.form['schoolSubjectSelect']
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO enseignant(nomEnseignant, prenomEnseignant,emailEnseignant, tel,specialite,nbr_groupe_enseigne) VALUES (%s, %s, %s, %s,%s,%s)",(lastName, firstName,  email, tel,matiere,0))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('professeur'))
        elif formation=='language' :
            langue=request.form['languageSelect'] 
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO enseignant(nomEnseignant, prenomEnseignant,emailEnseignant, tel,specialite,nbr_groupe_enseigne) VALUES (%s, %s, %s, %s,%s,%s)",(lastName, firstName,  email, tel,langue,0))
            mysql.connection.commit()
            cur.close()  
            return redirect(url_for('professeur'))
        else : 
            skill=request.form['SkillsSelect']  
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO enseignant(nomEnseignant, prenomEnseignant,emailEnseignant, tel,specialite,nbr_groupe_enseigne) VALUES (%s, %s, %s, %s,%s,%s)",(lastName, firstName,  email, tel,skill,0))
            mysql.connection.commit()
            cur.close()  
            return redirect(url_for('professeur'))
    return render_template('addprof.html')

@app.route('/viewstudent',methods=['GET', 'POST'])
def viewstudent():
    nbrskill=0 ;  nbrlangue=0 ; nbrmatiere=0; 
    eleve_info_langue=()   
    eleve_info_matiere=()  
    eleve_info_skill=()   
    if request.method=='POST':
        cur=mysql.connection.cursor()
        prenom=request.form['First_Name']
        nom=request.form['Last_Name']
        cur.execute(""" SELECT G.formation
                        FROM Groupe G
                        JOIN integrer I ON G.idGrp = I.idGrp
                        JOIN eleve E ON I.idElv = E.idElv
                        WHERE E.nomEleve = %s AND E.prenomEleve = %s;""", (nom, prenom))
        formation_groupe = cur.fetchall()

        for i in range (len(formation_groupe)):
            if formation_groupe[i][0] in ['C','C++','Python'] and nbrskill==0:   #   i pour ne pas repeter l'affichage d'un skill 
                cur.execute('''SELECT E.idElv, E.nomEleve, E.prenomEleve, E.tel, E.emailEleve, E.niveauScolaire,
                            G.idGrp, G.numGrp,  G.formation,
                            S.nbr_séances_restantes, S.nbr_séances_abscentes
                            FROM eleve E, integrer I, groupe G, absences_s S ,skills
                            WHERE E.idElv = I.idElv
                            AND I.idGrp = G.idGrp
                            AND E.idElv = S.idElv
                            and skills.idSkills=S.idSkills
                            AND G.formation IN ('C', 'C++', 'Python') 
                            and g.formation=skills.nomSkills
                            AND E.nomEleve = %s
                            AND E.prenomEleve = %s;''',(nom,prenom,))
                eleve_info_skill=cur.fetchall()
                nbr=1
                # return render_template('viewstudent.html',eleve_info=eleve_info)
            
            if formation_groupe[i][0] in ['English','French','Spanish'] and nbrlangue==0 :
                cur.execute('''SELECT E.idElv, E.nomEleve, E.prenomEleve, E.tel, E.emailEleve, E.niveauScolaire,
                            G.idGrp, G.numGrp,  G.formation,
                            l.nbr_séances_restantes, l.nbr_séances_abscentes    
                            FROM eleve E, integrer I, groupe G, absences_l l ,langue
                            WHERE E.idElv = I.idElv
                            AND I.idGrp = G.idGrp
                            AND E.idElv = l.idElv
                            and langue.idLangue = l.idLangue
                            AND G.formation IN ('English','French','Spanish') 
                            and g.formation = langue.nomLangue
                            AND E.nomEleve = %s
                            AND E.prenomEleve = %s;''',(nom,prenom,))
                eleve_info_langue=cur.fetchall()
                nbr=1
                print('succes')
                # return render_template('viewstudent.html',eleve_info=eleve_info)
            
            if formation_groupe[i][0] in ['French 1st','English 2nd','Maths','PC','Arabic','History','Islamic Education','Philo'] and nbrmatiere==0 :
                cur.execute('''SELECT E.idElv, E.nomEleve, E.prenomEleve, E.tel, E.emailEleve,E.niveauScolaire,
                            G.idGrp, G.numGrp,  G.formation,
                            m.nbr_séances_restantes, m.nbr_séances_abscentes
                            FROM eleve E, integrer I, groupe G, absences_m m ,matiere
                            WHERE E.idElv = I.idElv
                            AND I.idGrp = G.idGrp
                            AND E.idElv = l.idElv
                            and matiere.idMatiere = m.idMatiere
                            AND G.formation IN ('English 2nd','French 1st','Maths','PC','Arabic','History','Islamic Education','Philo')
                            and g.formation = langue.nomLangue
                            AND E.nomEleve = %s
                            AND E.prenomEleve = %s;''',(nom,prenom,))
                eleve_info_matiere=cur.fetchall()
                nbr=1    
        return render_template('viewstudent.html',eleve_info_skill=eleve_info_skill,eleve_info_langue=eleve_info_langue,eleve_info_matiere=eleve_info_matiere)        
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM eleve ORDER BY idElv;")
    eleves=cur.fetchall()
    return render_template('viewstudent.html',eleves=eleves,condition="true")
    
@app.route('/modifynewformation',methods=['GET', 'POST'])
def modifyStudent():
    if request.method=='POST':
        id=request.form['Id']
        formation =request.form['formation']
        mode=request.form['mod']
        if mode =='test':
            nbr_seance=1
            pay=paiment(nbr_seance,mode)
        else :                                                      # pour le paiment 
            nbr_seance=request.form['nbrSeance1']  
            pay=paiment(nbr_seance,mode)  
                        
        if formation == 'language' : 
            language = request.form['languageSelect'] # french / english / spanish 
            cur = mysql.connection.cursor()
            print(id)
            cur.execute("SELECT * from langue where nomLangue = (%s)",(language,))
            id_langue=cur.fetchall()[0][0]
            print(id_langue)
            cur.execute("INSERT INTO absences_l (idElv,idLangue,nbr_séances,nbr_séances_restantes,nbr_séances_abscentes) VALUES (%s,%s,%s,%s,%s)",(id,id_langue,nbr_seance,nbr_seance,0,))
            mysql.connection.commit()
            id_groupe=request.form['Id_group']
            cur.execute("insert into  integrer (idElv,idGrp) values(%s,%s)",(id,id_groupe,))
            mysql.connection.commit()
            cur.execute("update groupe set nbr_eleve =nbr_eleve +1  where idGrp=%s;",(id_groupe,))
            mysql.connection.commit()
            cur.close()
            return 'modification effectue '
        elif formation == 'schoolSupport' : 
            niveau = request.form['schoolLevelSelect']
            matiere = request.form['schoolSubjectSelect'] 
            cur = mysql.connection.cursor()
            print(id)
            cur.execute("SELECT * from matiere where nomMatiere = (%s)",(matiere,))
            id_matiere=cur.fetchall()[0][0]
            cur.execute("INSERT INTO absences_m (idElv,idMatiere,nbr_séances,nbr_séances_restantes,nbr_séances_abscentes) VALUES (%s,%s,%s,%s,%s)",(id,id_matiere,nbr_seance,nbr_seance,0,))
            mysql.connection.commit()
            id_groupe=request.form['Id_group']
            cur.execute("insert into  integrer (idElv,idGrp) values(%s,%s)",(id,id_groupe,))
            mysql.connection.commit()
            cur.execute("update groupe set nbr_eleve =nbr_eleve +1  where idGrp=%s;",(id_groupe,))
            mysql.connection.commit()
            cur.close()
            return 'modification effectue '
        else: 
            skill = request.form['SkillsSelect'] 
            cur = mysql.connection.cursor()
            print(id)
        try:
            cur.execute("SELECT * from skills where nomSkills = (%s)", (skill,))
            id_skills = cur.fetchall()[0][0]

            cur.execute("INSERT INTO absences_s (idElv, idSkills, nbr_séances, nbr_séances_restantes, nbr_séances_abscentes) VALUES (%s, %s, %s, %s, %s)", (id, id_skills, nbr_seance, nbr_seance, 0,))

            id_groupe = request.form['Id_group']
            cur.execute("INSERT INTO integrer (idElv, idGrp) VALUES (%s, %s)", (id, id_groupe))
            mysql.connection.commit()
            cur.execute("update groupe set nbr_eleve =nbr_eleve +1  where idGrp=%s;",(id_groupe,))
            mysql.connection.commit()
            cur.close()
            return 'Modification effectuée'

        except Exception as e:
                mysql.connection.rollback()
                cur.close()
                return f"Une erreur est survenue : {str(e)}"
    return render_template('modifynewformation.html') 

@app.route('/deletestudent',methods=['GET', 'POST'])
def deletestudent():
    
    tables = ['absences_s', 'absences_m', 'absences_l', 'integrer']
    if request.method=='POST':
        cur=mysql.connection.cursor()
        id=request.form['Id']
        for table in tables:
            cur.execute(f"delete from {table} where idElv = (%s)",(id,))
            mysql.connection.commit()
        cur.execute("select idGrp from integrer where idElv=%s",(id,))
        id_groupe=cur.fetchall()[0]   
        cur.execute("DELETE FROM eleve WHERE idElv = %s", (id,))
        mysql.connection.commit()
        cur.execute("update groupe set nbr_eleve =nbr_eleve -1  where idGrp=%s;",(id_groupe,))
        mysql.connection.commit()
        cur.close()
        
    return render_template('delet.html',Student_prof="Student")

@app.route('/addproftogroup',methods=['GET','POST'])
def addproftogroup():
    if request.method =='POST':
        id=request.form['Id']
        num_g=request.form['number']
        formation = request.form['formation']
        if formation=='schoolSupport':
            niveau=request.form['schoolLevelSelect']
            matiere=request.form['schoolSubjectSelect']
            cur = mysql.connection.cursor()
            cur.execute("select  specialite from enseignant where idEnseignant = (%s)",(id))
            spec_prof=cur.fetchall()[0]
            cur.execute("UPDATE groupe SET idEnseignant =(%s)  WHERE numGrp =(%s) and niveauScolaire=(%s) and formation=(%s)",(id,num_g,niveau,spec_prof))
            mysql.connection.commit()
            cur.execute("update enseignant set nbr_groupe_enseigne =nbr_groupe_enseigne +1  where idEnseignant=%s;",(id,))
            mysql.connection.commit()
            cur.close()
        elif formation=='language':
            langue=request.form['languageSelect']
            cur = mysql.connection.cursor()
            cur.execute("select  specialite from enseignant where idEnseignant = (%s)",(id,))
            spec_prof=cur.fetchall()[0]
            cur.execute("UPDATE groupe SET idEnseignant =(%s)  WHERE numGrp =(%s)  and formation=(%s)",(id,num_g,spec_prof))
            mysql.connection.commit()
            cur.execute("update enseignant set nbr_groupe_enseigne =nbr_groupe_enseigne +1  where idEnseignant=%s;",(id,))
            mysql.connection.commit()
            cur.close()    
           
        else : 
            skill=request.form['SkillsSelect']
            cur = mysql.connection.cursor()
            cur.execute("select  specialite from enseignant where idEnseignant = (%s)",(id,))
            spec_prof=cur.fetchall()[0]
            cur.execute("UPDATE groupe SET idEnseignant =(%s)  WHERE numGrp =(%s)  and formation=(%s)",(id,num_g,spec_prof,))
            mysql.connection.commit()
            cur.execute("update enseignant set nbr_groupe_enseigne = nbr_groupe_enseigne +1  where idEnseignant=%s;",(id,))
            mysql.connection.commit()
            cur.close() 
    return render_template('addproftogroup.html')

@app.route('/viewprof',methods=['GET', 'POST'])
def viewprof():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        nom=request.form['LastName']
        prenom=request.form['FirstName']
        cur.execute('''SELECT 
                    en.nomEnseignant,
                    en.prenomEnseignant,
                    en.specialite,
                    g.numGrp,
                    g.niveauScolaire
                    FROM enseignant en, groupe g
                    WHERE en.idEnseignant = g.idEnseignant
                    and nomEnseignant like %s or  prenomEnseignant like %s ''',(f"%{nom}%", f"%{prenom}%"))
        prof=cur.fetchall()
        return render_template('viewprof.html',prof=prof)
    cur.execute("select * from enseignant ")
    profs=cur.fetchall()
    cur.close()
    return render_template('viewprof.html',profs=profs,condition='true')

@app.route('/deleteprof',methods=['GET', 'POST'])
def deleteprof():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        id=request.form['Id']
        cur.execute(f"delete from groupe where idEnseignant = (%s)",(id,))
        mysql.connection.commit()
        cur.execute("DELETE FROM enseignant WHERE idEnseignant = %s", (id,))
        mysql.connection.commit()
        cur.close()
    return render_template('delet.html',Student_prof="Prof")

@app.route('/addgroup', methods=['GET', 'POST'])
def addgroup():
    if request.method == 'POST':
        formation = request.form['formation']
        if formation == 'schoolSupport':
            niveau = request.form['schoolLevelSelect']
            matiere = request.form['schoolSubjectSelect']
            cur = mysql.connection.cursor()
            cur.execute('''SELECT MAX(numGrp) FROM Groupe WHERE formation = %s and niveauScolaire=%s;''', (matiere, niveau,))
            max_num = cur.fetchone()
            if max_num[0] is None:
                max_num = (0,)
            cur.execute("insert into groupe (numGrp,niveauScolaire,formation,nbr_eleve) values (%s,%s,%s,%s)", (int(max_num[0]) + 1, niveau, matiere, 0))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('viewgroup'))
        elif formation == 'language':
            langue = request.form['languageSelect']
            cur = mysql.connection.cursor()
            cur.execute('''SELECT MAX(numGrp) FROM Groupe WHERE formation = %s ;''', (langue,))
            max_num = cur.fetchone()
            if max_num[0] is None:
                max_num = (0,)
            cur.execute("insert into groupe (numGrp,formation,nbr_eleve) values (%s,%s,%s)", (int(max_num[0]) + 1, langue, 0))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('viewgroup'))
        else:
            skill = request.form['SkillsSelect']
            cur = mysql.connection.cursor()
            cur.execute('''SELECT MAX(numGrp) FROM Groupe WHERE formation = %s ;''', (skill,))
            max_num = cur.fetchone()
            if max_num[0] is None:
                max_num = (0,)
            cur.execute("insert into groupe (numGrp,formation,nbr_eleve) values (%s,%s,%s)", (int(max_num[0]) + 1, skill, 0))
            mysql.connection.commit()
            cur.close()
            flash('Groupe ajouté avec succès!')
            return redirect(url_for('viewgroup'))

    return render_template('addgroup.html')

@app.route('/viewgroup',methods=['GET', 'POST'])
def viewgroup():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        group_num=request.form['groupe_number']
        niveau=request.form['schoolLevelSelect']
        formation=request.form['formation']
        if niveau=='none':
            cur.execute('''SELECT E.idElv ,E.nomEleve, E.prenomEleve
                            FROM eleve E
                            INNER JOIN integrer I ON E.idElv = I.idElv
                            INNER JOIN groupe G ON I.idGrp = G.idGrp
                            WHERE G.numGrp = %s  AND G.formation = %s''',(group_num,formation,))
            list_elv=cur.fetchall()
            return render_template('viewgroup.html',list_elv=list_elv)
        else :
            cur.execute('''SELECT E.idElv,E.nomEleve, E.prenomEleve
                            FROM eleve E
                            INNER JOIN integrer I ON E.idElv = I.idElv
                            INNER JOIN groupe G ON I.idGrp = G.idGrp
                            WHERE G.numGrp = %s AND G.niveauScolaire = %s AND G.formation = %s''',(group_num,niveau,formation,))
            list_elv=cur.fetchall()
            return render_template('viewgroup.html',list_elv=list_elv)
    cur.execute("select * from groupe ;")
    groups=cur.fetchall()
    cur.close()
    return render_template('viewgroup.html',groups=groups,condition ='true')

@app.route('/addseance',methods=['GET', 'POST'])
def addseance():
    if request.method=='POST':
        salle=request.form['Num_salle']
        date = datetime.strptime(request.form['Date_Seance'],'%Y-%m-%d') 
        heur_d=request.form['heure debut']
        heur_f=request.form['heure fin'] 
        n_groupe=request.form['num group']
        formation=request.form['formation']
        if formation=='language':
            langue=request.form['languageSelect']
            cur=mysql.connection.cursor()
            cur.execute("select idGrp from groupe where numGrp =(%s) and formation =(%s) and nbr_eleve >=4 ",(n_groupe,langue))
            id=cur.fetchall()
            if len(id) == 0:
                return "nbr d'eleve inferieur a 4 "
            for i in range(4):
                new_date = date + timedelta(weeks=i)
                cur.execute("select * from seance where salle=%s and dateSeance=%s and heureD =%s and heureF =%s", (salle, new_date.strftime('%Y-%m-%d'), heur_d, heur_f,))
                list_seance = cur.fetchall()
                if len(list_seance) > 0:
                    return f"Séance déjà programmée pour la semaine {i + 1}"
                cur.execute("insert into seance(dateSeance,heureD,heureF,idGrp,salle,formation) values(%s,%s,%s,%s,%s,%s)", (new_date.strftime('%Y-%m-%d'), heur_d, heur_f, id[0][0], salle, langue))
                mysql.connection.commit()
            cur.close()    
            return 'Séances programmées pour les quatre prochaines semaines'
        elif formation=='softSkills':
            skill=request.form['SkillsSelect']
            cur=mysql.connection.cursor()
            cur.execute("select idGrp from groupe where numGrp =(%s) and formation =(%s)",(n_groupe,skill,))
            id= cur.fetchall()
            if len(id) == 0:
                return "impossible de palnnifier cette seance nbr d'eleve inferieur a 4  "
            for i in range(4):
                new_date = date + timedelta(weeks=i)
                cur.execute("select * from seance where salle=%s and dateSeance=%s and heureD =%s and heureF =%s", (salle, new_date.strftime('%Y-%m-%d'), heur_d, heur_f,))
                list_seance = cur.fetchall()
                if len(list_seance) > 0:
                    return f"Séance déjà programmée pour la semaine {i + 1}"
                cur.execute("insert into seance(dateSeance,heureD,heureF,idGrp,salle,formation) values(%s,%s,%s,%s,%s,%s)", (new_date.strftime('%Y-%m-%d'), heur_d, heur_f, id[0][0], salle, skill))
                mysql.connection.commit()
            cur.close()    
            return 'Séances programmées pour les quatre prochaines semaines'
        else :  
            niveau = request.form['schoolLevelSelect'] 
            matiere =request.form['schoolSubjectSelect']  
            cur=mysql.connection.cursor()
            cur.execute("select idGrp from groupe where numGrp =(%s) and formation =(%s) and niveauScolaire =(%s)",(n_groupe,matiere,niveau))
            id=cur.fetchall()
            if len(id) == 0:
                return " impossible de palnnifier cette seance nbr d'eleve inferieur a 4 "
            for i in range(4):
                new_date = date + timedelta(weeks=i)
                cur.execute("select * from seance where salle=%s and dateSeance=%s and heureD =%s and heureF =%s", (salle, new_date.strftime('%Y-%m-%d'), heur_d, heur_f,))
                list_seance = cur.fetchall()
                if len(list_seance) > 0:
                    return f"Séance déjà programmée pour la semaine {i + 1}"
                cur.execute("insert into seance(dateSeance,heureD,heureF,idGrp,salle,formation) values(%s,%s,%s,%s,%s,%s)", (new_date.strftime('%Y-%m-%d'), heur_d, heur_f, id[0][0], salle,matiere))
                mysql.connection.commit()
            cur.close()    
            return 'Séances programmées pour les quatre prochaines semaines'
    return render_template('addseance.html')

@app.route('/viewseance',methods=['GET', 'POST'])
def viewseance():
    if request.method=='POST':
        salle=request.form['salle']
        date=request.form['date']
        groupe_num=request.form['groupe']
        niveau=request.form['schoolLevelSelect']
        formation=request.form['formation']
        cur=mysql.connection.cursor() 
        cur.execute('''SELECT seance.idSeance, seance.dateSeance, seance.heureD, seance.heureF,
                            groupe.numGrp , groupe.niveauScolaire , seance.salle, seance.formation
                            FROM seance
                            INNER JOIN groupe ON seance.idGrp = groupe.idGrp
                            WHERE seance.salle = %s 
                            AND seance.dateSeance = %s 
                            AND groupe.numGrp = %s 
                            AND groupe.niveauScolaire = %s 
                            AND seance.formation = %s;''',(salle,date,groupe_num,niveau,formation,)) 
        seances=cur.fetchall()
        return str(seances)
    cur=mysql.connection.cursor()
    cur.execute('''SELECT seance.idSeance, seance.dateSeance, seance.heureD, seance.heureF,
                    groupe.numGrp , groupe.niveauScolaire , seance.salle, seance.formation
                    FROM seance
                    INNER JOIN groupe ON seance.idGrp = groupe.idGrp;'''
                    )
    seances=cur.fetchall()
    cur.close()
    return render_template('viewseance.html',seances=seances,condition='true')

@app.route('/markingabsence',methods=['GET', 'POST'])
def markingabsence():
    if request.method=='POST':
        num_gr=request.form['Num_group']
        formation=request.form['formation']
        niveau=request.form['schoolLevelSelect']
        date=request.form['Date']
        cur=mysql.connection.cursor()
        if niveau=='None':
            cur.execute("""SELECT eleve.idElv, eleve.nomEleve, eleve.prenomEleve, groupe.numGrp, groupe.formation
                            FROM eleve
                            JOIN integrer ON eleve.idElv = integrer.idElv
                            JOIN groupe ON integrer.idGrp = groupe.idGrp
                            JOIN seance ON groupe.idGrp = seance.idGrp
                            WHERE groupe.numGrp = %s AND groupe.formation = %s
                            AND seance.dateSeance = %s""",(num_gr,formation,date,))
            li=cur.fetchall()
            cur.close()
            session['list_eleve'] = list(li)
            return redirect(url_for('listeabsence'))
        else : 
            cur.execute("""SELECT eleve.idElv, eleve.nomEleve, eleve.prenomEleve, groupe.numGrp, groupe.formation 
            FROM eleve
            JOIN integrer ON eleve.idElv = integrer.idElv
            JOIN groupe ON integrer.idGrp = groupe.idGrp
            JOIN seance ON groupe.idGrp = seance.idGrp
            WHERE groupe.numGrp = %s 
            AND groupe.formation = %s
            AND eleve.niveauScolaire = %s  
            AND seance.dateSeance = %s""",(num_gr,formation,niveau,date,))
            li=cur.fetchall()
            cur.close()

    return render_template("markingabsence.html")

@app.route('/listeabsence',methods=['GET', 'POST'])
def listeabsence():
    cur=mysql.connection.cursor()
    list_eleve = session.get('list_eleve', [])
    list_eleve=tuple(list_eleve)
    # print(list_eleve)
    # print(list_eleve[0][3])
    # print(list_eleve[0][4])
    group_num=list_eleve[0][3]   ;     formation=list_eleve[0][4]
    cur.execute("select idGrp from groupe where numGrp=%s and formation =%s ;",(group_num,formation))
    id_group=cur.fetchone()
    # print("lid du groupe : ",id_group )
    if request.method=='POST':
        absent_students = request.form.getlist('absent_students')
        # print("ID des élèves absents:", absent_students)
        present_students=[eleve[0] for eleve in list_eleve if str(eleve[0]) not in absent_students]
        # print(present_students)
        # print(list_eleve[0][4])
        if list_eleve[0][4] in ['C','C++','Python']:
            cur.execute("select idSkills from skills where nomSkills =%s",(list_eleve[0][4],))
            id_skill=cur.fetchone()                    #id de skill 
            # print("id de ce skill est : ",id_skill)
            for student in absent_students:            # ici student va prendre l'id de eleve 
                # print("ce id est ",student)
                cur.execute('''UPDATE absences_s
                                SET nbr_séances_abscentes = nbr_séances_abscentes + 1
                                WHERE idElv = %s AND idSkills = %s;''',(student,id_skill,))
                mysql.connection.commit()
                cur.execute('''UPDATE absences_s
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idSkills = %s and nbr_séances_abscentes >= 2 ;''',(student,id_skill,))
                mysql.connection.commit()
                cur.execute("select nbr_séances_restantes,nbr_séances_abscentes  from absences_s where  idElv =%s and idSkills =%s",(student,id_skill,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
                if nbr_seance_restante <= -1 :
                    cur.execute("delete from integrer where idElv =%s and idGrp =%s",(student,id_group,))
                    mysql.connection.commit()
                    cur.execute("update groupe set nbr_eleve = nbr_eleve - 1  where idGrp =%s ",(id_group,))
                    mysql.connection.commit()
            for student in present_students:
                cur.execute('''UPDATE absences_s
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idSkills = %s ;''',(student,id_skill,))
                cur.execute("select nbr_séances_restantes from absences_s where  idElv =%s and idSkills =%s",(student,id_skill,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
            return redirect(url_for('seance'))
        elif list_eleve[0][4] in ['English','French','Spanish']:
            cur.execute("select idLangue from langue where nomLangue =%s",(list_eleve[0][4],))
            id_langue=cur.fetchone()                    #id de la langue  
            # print("id de cette langue  est : ",id_skill)
            for student in absent_students:            # ici student va prendre l'id de eleve 
                print("ce id est ",student)
                cur.execute('''UPDATE absences_l
                                SET nbr_séances_abscentes = nbr_séances_abscentes + 1
                                WHERE idElv = %s AND idLangue = %s;''',(student,id_langue,))
                mysql.connection.commit()
                cur.execute('''UPDATE absences_l
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idLangue = %s and nbr_séances_abscentes >= 2 ;''',(student,id_langue,))
                mysql.connection.commit()
                cur.execute("select nbr_séances_restantes,nbr_séances_abscentes  from absences_l where  idElv =%s and idLangue =%s",(student,id_langue,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
                if nbr_seance_restante < -1 :
                    cur.execute("delete from integrer where idElv =%s and idGrp =%s",(student,id_group,))
                    mysql.connection.commit()
                    cur.execute("update groupe set nbr_eleve = nbr_eleve - 1  where idGrp =%s ",(id_group,))
                    mysql.connection.commit()
            for student in present_students:
                cur.execute('''UPDATE absences_l
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idSkills = %s ;''',(student,id_langue,))
                cur.execute("select nbr_séances_restantes from absences_l where  idElv =%s and idLangue =%s",(student,id_langue,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
            return redirect(url_for('seance'))
        else : 
            cur.execute("select idMatiere from matiere where nomMatiere =%s",(list_eleve[0][4],))
            id_matiere=cur.fetchone()                    #id de la matiere 
            # print("id de cette matiere  est : ",id_matiere)
            for student in absent_students:            # ici student va prendre l'id de eleve 
                # print("ce id est ",student)
                cur.execute('''UPDATE absences_m
                                SET nbr_séances_abscentes = nbr_séances_abscentes + 1
                                WHERE idElv = %s AND idMatiere = %s;''',(student,id_matiere,))
                mysql.connection.commit()
                cur.execute('''UPDATE absences_m
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idMatiere = %s and nbr_séances_abscentes >= 2 ;''',(student,id_matiere,))
                mysql.connection.commit()
                cur.execute("select nbr_séances_restantes,nbr_séances_abscentes  from absences_m where  idElv =%s and idMatiere =%s",(student,id_langue,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
                if nbr_seance_restante < -1 :
                    cur.execute("delete from integrer where idElv =%s and idGrp =%s",(student,id_group,))
                    mysql.connection.commit()
                    cur.execute("update groupe set nbr_eleve = nbr_eleve - 1  where idGrp =%s ",(id_group,))
                    mysql.connection.commit()
            for student in present_students:
                cur.execute('''UPDATE absences_m
                                SET nbr_séances_restantes =  nbr_séances_restantes - 1
                                WHERE idElv = %s AND idMatiere = %s ;''',(student,id_matiere,))
                cur.execute("select nbr_séances_restantes from absences_m where  idElv =%s and idMatiere =%s",(student,id_matiere,))
                nbr_seance=cur.fetchall()
                nbr_seance_restante=nbr_seance[0][0]
            return redirect(url_for('seance'))    
    return render_template('listeabsence.html',list_eleve=list_eleve)


@app.route('/addadmin',methods=['GET', 'POST'])
def addadmin():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        confirmPasword=request.form['password2']
        if confirmPasword!=password :
            return render_template('addadmin.html')
        cur=mysql.connection.cursor()
        cur.execute("insert into admin_c(gmail_admin,password_c) values (%s,%s)",(email,password))
        mysql.connection.commit()
        cur.close()
        return render_template('index_student.html')
    return render_template('addadmin.html')

@app.route('/deleteadmin',methods=['GET','POST'])
def deleteadmin():
    cur=mysql.connection.cursor()
    if request.method=='POST':
        id=request.form['Id']
        cur.execute('delete from admin_c where idAdmn = %s',(id,))
        mysql.connection.commit()
    cur.execute('select * from admin_c')
    admins=cur.fetchall()
    cur.close()
    return render_template('delet.html',admins=admins,condition='true',student_prof='admin')


    

#statistique de groupe eleve et ensignant 
#ajouter l'afectation a un groupe au cas ou l'eleve est exclus du groupe 

@app.route('/payment_renewal',methods=['GET','POST'])
def payment_renewal():
    
    if request.method=='POST':
        nom=request.form['lastName']
        prenom=request.form['firstName']
        email=request.form['email']
        formation=request.form['formation']
        nbr_seance=request.form['nbr_Seance']
        cur=mysql.connection.cursor()
        cur.execute("select idElv from eleve where nomEleve=%s and prenomEleve =%s and emailEleve =%s ",(nom,prenom,email,))
        id_eleve=cur.fetchone()
        print("l'id de l'eleve est :",id_eleve)
        if formation=='language':
            langue=request.form['languageSelect']
            cur.execute(" select idLangue from langue where nomLangue=%s",(langue,))
            id_langue=cur.fetchone()
            print("l'id de la langue  est :",id_langue)
            cur.execute("select nbr_séances_restantes from absences_l where idElv =%s and idLangue =%s ",(id_eleve,id_langue,))
            nbr_seances_restantes=cur.fetchone()
            print(nbr_seances_restantes[0])
            if int(nbr_seances_restantes[0]) <= 0:
                cur.execute("update absences_l set nbr_séances=%s , nbr_séances_restantes=%s where idElv =%s and idLangue =%s",(nbr_seance,nbr_seance,id_eleve,id_langue,))
                mysql.connection.commit()
                #ajouter le paiment 
                return redirect(url_for('student'))
        elif formation =='softSkills':
            Skills=request.form['SkillsSelect']
            cur.execute(" select idSkills from Skills where nomSkills=%s",(Skills,))
            id_Skills=cur.fetchone()
            print("l'id de la Skills  est :",id_Skills)
            cur.execute("select nbr_séances_restantes from absences_s where idElv =%s and idSkills =%s ",(id_eleve,id_Skills,))
            nbr_seances_restantes=cur.fetchone()
            print(nbr_seances_restantes[0])
            if int(nbr_seances_restantes[0]) <= 0:
                cur.execute("update absences_s set nbr_séances=%s , nbr_séances_restantes=%s where idElv =%s and idSkills =%s",(nbr_seance,nbr_seance,id_eleve,id_Skills,))
                mysql.connection.commit()
                return redirect(url_for('student'))
            return 'impossible de renouvler le contrat'
        else : 
            niveau=request.form['schoolLevelSelect']
            matiere=request.form['schoolSubjectSelect']
            cur.execute(" select idMatiere from matiere where nomMatiere=%s",(matiere,))
            id_matiere=cur.fetchone()
            cur.execute("select nbr_séances_restantes from absences_m where idElv =%s and idMatiere =%s ",(id_eleve,id_matiere,))
            nbr_seances_restantes=cur.fetchone()
            print(nbr_seances_restantes[0])
            if int(nbr_seances_restantes[0]) <= 0:
                cur.execute("update absences_m set nbr_séances=%s , nbr_séances_restantes=%s where idElv =%s and idMatiere =%s",(nbr_seance,nbr_seance,id_eleve,id_matiere,))
                mysql.connection.commit()
                return redirect(url_for('student'))
            return 'impossible de renouvler le contrat'
    return render_template('payment_renewal.html')
if __name__=="__main__":
    app.run(debug=True)



