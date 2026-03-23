def get_url_yt(url_yt):
	import requests
	import re    
	# Obtener el contenido del HTML
	response = requests.get(url_yt)
	#html_content = response.text
	# Usar una expresión regular para encontrar la URL que deseas
	url_pattern = re.compile(r'https://manifest\.googlevideo\.com/api/manifest/hls_variant/.*?index\.m3u8')
	return url_pattern.findall(response.text)


def update_url_yt (url_yt):
	import requests
	import json
	from ALR_Casa import print_terminal
	
	# URL del HTML que contiene la URL que quieres capturar
	html_url = url_yt
	matched_urls = get_url_yt(html_url)
	if matched_urls:
		hls_url = matched_urls[0]
		print_terminal("URL capturada correctamente")
	else:
		print_terminal("No se encontró la URL en el contenido HTML.")    
		hls_url = "https://skynewsau-live.akamaized.net/hls/live/2002689/skynewsau-extra1/master.m3u8?ref=developerinsider.co"              
	return hls_url