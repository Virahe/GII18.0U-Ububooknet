# -*- coding: utf-8 -*-
import os
import re
from flask import render_template, Flask, request, url_for, redirect, json
from src import modelo as mod
import zipfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.dirname(os.path.realpath(__file__))+"\\ficheros"

m = mod.modelo.getInstance()

@app.route('/', methods=["GET","POST"])
def index():
    error = ''
    if request.method == "POST":
        if("btn btn-selepub" not in request.files):
            error = "No se ha seleccionado ningún fichero"
            return render_template('index.html', error = error)
        fich = request.files["btn btn-selepub"]
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], fich.filename)
        fich.save(fullpath)
        if(zipfile.is_zipfile(fullpath)):
            if("btn btn-cargarepub" in request.form):
                m.obtTextoEpub(fullpath)
                m.vaciarDiccionario()
                return redirect(url_for('dictaut'))
        else: 
            error = "La ruta indicada no contiene un fichero epub"
            return render_template('index.html', error = error)
    return render_template('index.html')

@app.route('/Dicts-Automaticos/', methods=["GET", "POST"])
def dictaut():
    msg = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        if("cbx cbx-vacdit"  in request.form):
            m.vaciarDiccionario()
        if("btn btn-creadict" in request.form):
            m.crearDict()
            msg = "Diccionario creado con éxito"
        elif("btn btn-impdict" in request.form):
            return redirect(url_for('impdict'))
        elif("btn btn-obtdict" in request.form):
            return redirect(url_for('obtdict'))
    return render_template('dictaut.html', msg = msg)

@app.route('/Dicts-Automaticos/Importar-Dict/', methods=["GET","POST"])
def impdict():
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    error = ''
    if request.method == "POST":
        if("btn btn-selcsv" not in request.files):
            error = "No se ha seleccionado ningún fichero"
            return render_template('impdict.html', error = error)
        fich = request.files["btn btn-selcsv"]
        fullpath = os.path.join(app.config['UPLOAD_FOLDER'], fich.filename)
        fich.save(fullpath)
        if("btn btn-cargarcsv" in request.form):
            #Se deja para futuros sprint comprobar que el fichero introducido es csv
            # debido a que mimetype no reconoce si el archivo es csv
            if(True):
                m.importDict(fullpath)
                error = "Fichero csv cargado"
            else: 
                error = "La ruta indicada no contiene un fichero csv"
    return render_template('impdict.html', error = error)

@app.route('/Dicts-Automaticos/Obtener-Dict/', methods=["GET","POST"])
def obtdict():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        url = request.form['txt txt-url']
        if(len(url)>0):
            m.scrapeWiki(url)
            error = 'Se han introducido correctamente los personajes de la url'
            #Se deja para futuros sprints comprobar que la url contenía información scrapeable
        else:
            error = 'No se permiten textos vacíos como url'
    return render_template('obtdict.html', error = error)

@app.route('/Modificar-Diccionario/', methods=["GET", "POST"])   
def moddict():
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        if("btn btn-newpers" in request.form):
            return redirect(url_for('newpers'))
        elif("btn btn-delpers" in request.form):
            return redirect(url_for('delpers'))
        elif("btn btn-joinpers" in request.form):
            return redirect(url_for('joinpers'))
        elif("btn btn-newrefpers" in request.form):
            return redirect(url_for('newrefpers'))
        elif("btn btn-delrefpers" in request.form):
            return redirect(url_for('delrefpers'))
        elif("btn btn-modid" in request.form):
            return redirect(url_for('modidpers'))
        elif("btn btn-parseo" in request.form):
            m.prepararRed()
            return redirect(url_for('params'))
    return render_template('moddict.html', pers = m.getPersonajes())

@app.route('/Modificar-Diccionario/Anadir-Personaje/', methods=["GET", "POST"])    
def newpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        idperso = request.form['txt txt-idpers']
        perso = request.form['txt txt-nombrepers']
        if(len(perso)>0 and len(idperso)>0):
            error = m.anadirPersonaje(idperso,perso)
        else:
            error = 'No se permiten textos vacíos como nombre de personaje'
    return render_template('newpers.html', error = error, pers = m.getPersonajes())

@app.route('/Modificar-Diccionario/Eliminar-Personaje/', methods=["GET", "POST"])    
def delpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        perso = request.form['txt txt-idpers']
        if(len(perso)>0):
            if(m.eliminarPersonaje(perso)):
                error = 'Se ha eliminado correctamente el personaje'
            else:
                error = 'No existe ningún personaje con esa id'
        else:
            error = 'No se permiten textos vacíos como id de personaje'
    return render_template('delpers.html', error = error, pers = m.getPersonajes())

@app.route('/Modificar-Diccionario/Juntar-Personajes/', methods=["GET", "POST"])    
def joinpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        id1p = request.form['txt txt-id1pers']
        id2p = request.form['txt txt-id2pers']
        if(len(id1p)>0 and len(id2p)>0):
            if(m.juntarPersonajes(id1p,id2p)):
                error = 'Los personajes se han juntado con éxito'
            else:
                error = 'Una o ambas ids son erroneas'
        else:
            error = 'No se permiten textos vacíos como id de personaje o nueva referencia'
    return render_template('joinpers.html', error = error, pers = m.getPersonajes())
   
@app.route('/Modificar-Diccionario/Nueva-Referencia/', methods=["GET", "POST"])    
def newrefpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        idp = request.form['txt txt-idpers']
        ref = request.form['txt txt-refpers']
        if(len(idp)>0 and len(ref)>0):
            if(m.anadirReferenciaPersonaje(idp,ref)):
                error = 'Referencia añadida con éxito'
            else:
                error = 'La id no existe o esa referencia ya pertenece a ese personaje'
        else:
            error = 'No se permiten textos vacíos como id de personaje o nueva referencia'
    return render_template('newrefpers.html', error = error, pers = m.getPersonajes())

@app.route('/Modificar-Diccionario/Eliminar-Referencia/', methods=["GET", "POST"])    
def delrefpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        idp = request.form['txt txt-idpers']
        ref = request.form['txt txt-refpers']
        if(len(idp)>0 and len(ref)>0):
            if(m.eliminarReferenciaPersonaje(idp,ref)):
                error = 'Se ha eliminado correctamente la referencia'
            else:
                error = 'La id o la referencia no existe'
        else:
            error = 'No se permiten textos vacíos como id de personaje o nueva referencia'
    return render_template('delrefpers.html', error = error, pers = m.getPersonajes())

@app.route('/Modificar-Diccionario/Cambiar-Identificador/', methods=["GET", "POST"])
def modidpers():
    error = ''
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        idact = request.form['txt txt-idact']
        newid = request.form['txt txt-newid']
        if(len(idact)>0 and len(newid)>0):
            error = m.modificarIdPersonaje(idact,newid)
        else:
            error = 'No se permiten textos vacíos como id de personaje'
    return render_template('modidpers.html', error = error, pers = m.getPersonajes())
    
@app.route('/Parametros/', methods=["GET", "POST"])
def params():
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    error1 = ''
    error2 = ''
    num = re.compile('[0-9]+')
    if request.method == "POST":
        if("btn btn-red" in request.form):
            apar = request.form['txt txt-apar']
            dist = request.form['txt txt-dist']
            if(len(apar)>0 and len(dist)>0 and num.match(apar).group()==apar and num.match(dist).group()==dist):
                m.generarGrafo(int(dist),int(apar))           
                return redirect(url_for('red'))
            else:
                if(len(apar)==0):
                    error1 = 'Introduzca el número mínimo de apariciones para que aparezca un personaje en la red'
                elif(num.match(apar) == None or num.match(apar).group()!=apar):
                    error1 = 'Introduzca unicamente dígitos del 0 al 9'
                if(len(dist)==0):
                    error2 = 'Introduzca la distancia máxima para que se considere que hay relación entre dos personajes'
                elif(num.match(dist) == None or num.match(dist).group()!=dist):
                    error2 = 'Introduzca unicamente dígitos del 0 al 9'
    return render_template('params.html', error1 = error1, error2 = error2)

@app.route('/Red/', methods=["GET", "POST"])
def red():
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    jsonred = m.visualizar()
    return render_template('red.html', jsonred = jsonred)

@app.route('/Informe/', methods=["GET", "POST"])
def informe():
    if(m.getTexto() == ''):
        return redirect(url_for('index'))
    if request.method == "POST":
        if("btn btn-vis" in request.form):
            print('Visualizar')
    return render_template('informe.html')