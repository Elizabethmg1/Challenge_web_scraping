import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pymysql

#funcion de apostrofe doble para evitar el error de sintaxis en sql
def apostrofe_doble(param1:str)->str:
    texto=''
    for caracter in param1:
        if caracter=='\'':
            texto+='\''
        texto+=caracter
    return texto

#conexion a la base de datos sql
connection=pymysql.connect(
    host="localhost",
    user="root",
    password="",
    db="datosproyecto")

cursor=connection.cursor()

s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()

driver.get('https://yts.mx/browse-movies')

for pagina in range(1,1960):
    #Todas las peliculas en una lista
    peliculas=driver.find_elements(By.XPATH,'//div[@class="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4"]')
    
    numPelicula=1
    for pelicula in peliculas:
        # click en el primer enlace y se abre una pestaña nueva
        tab=driver.find_element(By.XPATH,"/html/body/div[4]/div[4]/div/section/div/div[" + str(numPelicula)  +"]/div/a")
        tab.send_keys(Keys.CONTROL + Keys.RETURN)

        # se hace foco sobre la nueva pestaña
        driver.switch_to.window(driver.window_handles[1])

        #en el caso de abrirse publicidad, vuelve a intentar clickear la pelicula
        if 'https://yts.mx/movies/' not in driver.current_url:
            # Cerrar la nueva pestaña de URL-secundaria
            driver.close()
            # Cambiar el foco, para volver a la URL-principal
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)
            # click en el primer enlace y se abre una pestaña nueva
            tab=driver.find_element(By.XPATH,"/html/body/div[4]/div[4]/div/section/div/div[" + str(numPelicula)  +"]/div/a")
            tab.send_keys(Keys.CONTROL + Keys.RETURN)

            # se hace foco sobre la nueva pestaña
            driver.switch_to.window(driver.window_handles[1])

        time.sleep(1)

        #busqueda y guardado de datos
        try:
            comentariosConcatenados=""
            comentarios=driver.find_elements(By.XPATH,'.//div[@class="comment-text"]')
            for comentario in comentarios:
                textoComentario=comentario.find_element(By.XPATH,'.//p').text
                comentariosConcatenados+=textoComentario + "-"
                #print(textoComentario)
            #print(comentariosConcatenados)
            
            titulo=driver.find_element(By.XPATH,'.//div[@class="hidden-xs"]//h1').text
            anio=driver.find_element(By.XPATH,'.//div[@class="hidden-xs"]//h2[1]').text
            sipnosis=driver.find_element(By.XPATH,'.//p[@class="hidden-xs"]').text
            enlaceWeb=driver.current_url
            generos=driver.find_element(By.XPATH,'.//div[@class="hidden-xs"]//h2[2]').text
            likes=driver.find_element(By.XPATH,'.//span[@id="movie-likes"]').text
            ratingImdb=driver.find_element(By.XPATH,'.//span[@itemprop="ratingValue"]').text
            
            
            #print(titulo + " \n"+ anio + " \n"+ sipnosis + " \n"+ enlaceWeb+ " \n"+ generos+ " \n"+ likes + " \n" + ratingImdb)

             #insertando informacion a la base de datos sql
            sql="INSERT INTO Peliculas (titulo,anio,sipnosis,enlaceWeb,generos,likes,ratingImdb,comentarios) VALUES('" + apostrofe_doble(titulo) + "','" + anio[0:5] + "','" + apostrofe_doble(sipnosis) + "','" + enlaceWeb + "','" + generos + "','" + likes +"','"+ ratingImdb +"','"+ apostrofe_doble(comentariosConcatenados) +"');"
            cursor.execute(sql)
            connection.commit()
        
        except Exception as e:
            print(e)
        
        # Cerrar la nueva pestaña de URL-secundaria
        driver.close()
        # Cambiar el foco, para volver a la URL-principal
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)

        numPelicula+=1 

    if pagina !=1959:
        try:
            #obtener el link del boton para cambiar de pagina
            link_btn_pagina = driver.find_element(By.PARTIAL_LINK_TEXT,'Next')
            driver.execute_script("arguments[0].click();", link_btn_pagina)
            sleep(random.uniform(8.0,10.0))
        except Exception as ex:
            print(ex)
