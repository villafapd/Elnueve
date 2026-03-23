def yt_url_base(canaltv):
	#from ALR_Casa import mariadb
	import mariadb
	# Abrir el archivo de texto en modo lectura
	with open("/home/villafapd/Documents/ConfigEspeciales/BotTelegram.txt", "r") as archivo:
		# Leer las líneas del archivo
		lineas = archivo.readlines()
	# Inicializar las variables
	USER = ""
	PASSWORD = ""
	# Procesar las lineas del archivo
	for linea in lineas:
		if linea.startswith("USER"):
			USER = linea.split("=")[1].strip().strip("'")
		elif linea.startswith("PASSWORD"):
			PASSWORD = linea.split("=")[1].strip().strip("'")
   
	query = "SELECT url_yt FROM {} WHERE {} = {}".format('Multimedia', 'id_multimedia', canaltv)
	with mariadb.connect(user=USER, password=PASSWORD, database="homeserver") as conn:
		with conn.cursor() as cur:
			cur.execute(query)
			#conn.commit()
			while True:
				row = cur.fetchone() #cur.fetchall()
				if row is None:
					break
				url = row[0]
		conn.commit()
	return url


def get_url_yt(url_yt):
	import requests
	import re    
	# Obtener el contenido del HTML
	response = requests.get(url_yt)
	#html_content = response.text
	# Usar una expresión regular para encontrar la URL que deseas
	url_pattern = re.compile(r'https://manifest\.googlevideo\.com/api/manifest/hls_variant/.*?index\.m3u8')
	return url_pattern.findall(response.text)
	
def yt_to_m3u8(yt_url_base, nombre_canal):    
	# Obtener el contenido del HTML
	matched_urls = get_url_yt(yt_url_base)
	# Si encuentras la URL, la imprimes
	if matched_urls:
		url_m3u8 = matched_urls[0]
		nombre = "URL capturada correctamente para " + nombre_canal
		return nombre, url_m3u8
	else:
		nombre = "No se encontró la URL para " + nombre_canal
		return nombre,"ttps://skynewsau-live.akamaized.net/hls/live/2002689/skynewsau-extra1/master.m3u8?ref=developerinsider.co"
		

def update_url_tv (token, gist_id):
	import requests
	import json
	from ALR_Casa import print_terminal
	TNNOTICIAS = '1'
	CANAL7MZA = '2'
	CANAL26 = '3'
	LANANCION = '4'
	RTVE = '5'
	FRANCE24 = '6'
	TELEFENOT = '7'
	AMERICA24 = '8'
 
	url_TN = yt_url_base(TNNOTICIAS)
	print_TN, hls_url_TN = yt_to_m3u8(url_TN,'TN')
	print_terminal(print_TN)

	url_C7Mza = yt_url_base(CANAL7MZA)
	print_C7Mza, hls_url_C7Mza = yt_to_m3u8(url_C7Mza,'Canal 7 Mendoza')
	print_terminal(print_C7Mza)	

	url_canal26 = yt_url_base(CANAL26)	
	print_Canal26, hls_url_Canal26 = yt_to_m3u8(url_canal26, 'Canal 26')
	print_terminal(print_Canal26)	

	url_lanacion = yt_url_base(LANANCION)
	print_lanacion, hls_url_lanacion = yt_to_m3u8(url_lanacion, 'La Nacion +')
	print_terminal(print_lanacion)

	url_rtve = yt_url_base(RTVE)
	print_RTVE, hls_url_RTVE = yt_to_m3u8(url_rtve, 'RTVE')
	print_terminal(print_RTVE)  	

	url_france24 = yt_url_base(FRANCE24)
	print_France24, hls_url_France24 = yt_to_m3u8(url_france24, 'France 24')
	print_terminal(print_France24) 

	url_telefenoti = yt_url_base(TELEFENOT)
	print_TelefeNoti, hls_url_TelefeNoti = yt_to_m3u8(url_telefenoti, 'Telefe Noticias')
	print_terminal(print_TelefeNoti)

	url_america24 = yt_url_base(AMERICA24)
	print_am24, hls_url_am24 = yt_to_m3u8(url_america24, 'America 24')
	print_terminal(print_am24)


	 #Abro el archivo de la lista de canales 
	data = open('/home/villafapd/Documents/PythonProjects/MiCasaDomo/ListaTv/listaCanaleslocal.m3u').read()
	# Dividimos el contenido en líneas
	lines = data.split('\n')
	# Comprobamos si hay al menos 27 líneas y actualizamos la línea 26
	if len(lines) >= 26:
		lines[32] = hls_url_TN  # Actualizamos la línea
		updated_content = '\n'.join(lines)
		lines[5] = hls_url_C7Mza  # Actualizamos la línea
		updated_content = '\n'.join(lines)
		lines[29] = hls_url_am24  # Actualizamos la línea
		updated_content = '\n'.join(lines)
		lines[38] = hls_url_Canal26  # Actualizamos la línea
		updated_content = '\n'.join(lines)  
		lines[41] = hls_url_lanacion  # Actualizamos la línea
		updated_content = '\n'.join(lines) 
		lines[44] = hls_url_RTVE  # Actualizamos la línea
		updated_content = '\n'.join(lines)          
		lines[47] = hls_url_France24  # Actualizamos la línea
		updated_content = '\n'.join(lines)   
		lines[184] = hls_url_TelefeNoti  # Actualizamos la línea
		updated_content = '\n'.join(lines)  
	try:
		with open('/home/villafapd/Documents/PythonProjects/MiCasaDomo/ListaTv/listaCanaleslocal.m3u', 'w') as archivo:
			archivo.writelines(updated_content)
		print_terminal("Lista de canales actualizada y guardada correctamente.")
	except Exception as e: # Captura excepciones más generales para un mejor manejo de errores
		print_terminal(f"Error al guardar el archivo: {e}")


	paste_text = open('/home/villafapd/Documents/PythonProjects/MiCasaDomo/ListaTv/listaCanaleslocal.m3u').read()
	update_data = {
		"description": "ListaCanalesLocales",
		"files": {
			"ListaCanalesLocales.m3u": {
				"content": paste_text
			}
		}
	}

	response = requests.patch(
		f'https://api.github.com/gists/{gist_id}',
		headers={
			'Authorization': f'token {token}',
			'Content-Type': 'application/json; charset=utf-8'
		},
		data=json.dumps(update_data).encode('utf-8')
	)


#'Authorization': f'token {token}'},
#		data=json.dumps(update_data)
#	)

	if response.status_code == 200:
		print_terminal("Gist actualizado exitosamente!")
	else:
		print_terminal("Error al actualizar el Gist:", response.status_code)

#update_url_tv()
#yt_url_base('1')

import requests
from bs4 import BeautifulSoup

def obtener_url_en_vivo(nombre_canal):
    url = f'https://www.youtube.com/c/{nombre_canal}/live'
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Verifica si hay redirecci�n a una transmisi�n en vivo
    for meta in soup.find_all('meta'):
        if meta.get('property') == 'og:url':
            return meta.get('content')

    return None

# Ejemplo de uso
canal_en_vivo = obtener_url_en_vivo('canal26argentina')
print('? URL de transmisi�n en vivo:', canal_en_vivo)
