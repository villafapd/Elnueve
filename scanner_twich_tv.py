#Simple ejemplo para capturar url de canales de tv
#Usando geckordp se puede obtener la url de twich y llevarla a un reproductor de iptv
#Se requiere de Firefox V 135 (ARM64)
#Se requiere addons "Alternate player for twichtv" link:https://addons.mozilla.org/en-US/firefox/addon/twitch_5/
#Se usa "Alternate player for twichtv" porque es mas liviano para raspberry pi 4 y ademas no requiere loggin de twich para ciertos canales
#Se debe configurar en firefox ---> about:config
# 	media.geckoview.autoplay.request = True
# Para Carga del addons con el canal se debe usar el identificador unico del addons "Alternate Player for Twich"
# 	about:debugging#/runtime/this-firefox
# 		buscar "Internal UUID" en este caso "b06a910a-a14a-4f77-a09c-7a2a8c77e414" para mi navegador
# Se envian notificaciones a telegram 

import argparse
import json
from concurrent.futures import Future
from geckordp.actors.accessibility.accessibility import AccessibilityActor
from geckordp.actors.accessibility.accessible import AccessibleActor
from geckordp.actors.accessibility.accessible_walker import AccessibleWalkerActor
from geckordp.actors.accessibility.parent_accessibility import ParentAccessibilityActor
from geckordp.actors.accessibility.simulator import SimulatorActor
from geckordp.actors.addon.addons import AddonsActor
from geckordp.actors.addon.web_extension_inspected_window import (
	WebExtensionInspectedWindowActor,
)
from geckordp.actors.descriptors.process import ProcessActor
from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.descriptors.web_extension import WebExtensionActor
from geckordp.actors.descriptors.worker import WorkerActor
from geckordp.actors.device import DeviceActor
from geckordp.actors.events import Events
from geckordp.actors.heap_snapshot import HeapSnapshotActor
from geckordp.actors.inspector import InspectorActor
from geckordp.actors.memory import MemoryActor
from geckordp.actors.network_content import NetworkContentActor
from geckordp.actors.network_event import NetworkEventActor
from geckordp.actors.network_parent import NetworkParentActor
from geckordp.actors.node import NodeActor
from geckordp.actors.node_list import NodeListActor
from geckordp.actors.preference import PreferenceActor
from geckordp.actors.resources import Resources
from geckordp.actors.root import RootActor
from geckordp.actors.screenshot import ScreenshotActor
from geckordp.actors.source import SourceActor
from geckordp.actors.storage import (
	CacheStorageActor,
	CookieStorageActor,
	IndexedDBStorageActor,
	LocalStorageActor,
	SessionStorageActor,
)
from geckordp.actors.string import StringActor
from geckordp.actors.target_configuration import TargetConfigurationActor
from geckordp.actors.targets.content_process import ContentProcessActor
from geckordp.actors.targets.window_global import WindowGlobalActor
from geckordp.actors.thread import ThreadActor
from geckordp.actors.thread_configuration import ThreadConfigurationActor
from geckordp.actors.walker import WalkerActor
from geckordp.actors.watcher import WatcherActor
from geckordp.actors.web_console import WebConsoleActor
from geckordp.firefox import Firefox
from geckordp.profile import ProfileManager
from geckordp.rdp_client import RDPClient
import schedule
import time
from datetime import timedelta, datetime
import re
from functools import partial
from geckordp.settings import GECKORDP
import setproctitle
import requests
setproctitle.setproctitle("ServerDomo-ScanTwichTv")
Path_ListaTv_DomoCasa = "/home/villafapd/Documents/PythonProjects/MiCasaDomo/ListaTv/listaCanaleslocal.m3u" 
GECKORDP.DEBUG = 1
GECKORDP.DEBUG_REQUEST = 1
GECKORDP.DEBUG_RESPONSE = 1
GECKORDP.LOG_FILE = "xyz.log" #: enabled

# Abrir el archivo de texto en modo lectura
with open("/home/villafapd/Documents/ConfigEspeciales/BotTelegram.txt", "r") as archivo:
	# Leer las líneas del archivo
	lineas = archivo.readlines()
# Inicializar las variables
USER = ""
PASSWORD = ""
idBot = ""
idGrupo = ""
idmio = ""


# Procesar las lineas del archivo
for linea in lineas:
	if linea.startswith("idBot_CasaDanielBot"):
		idBot = linea.split("=")[1].strip().strip("'")
	elif linea.startswith("idGrupo"):
		idGrupo = linea.split("=")[1].strip().strip("'")
	elif linea.startswith("idmio"):
		idmio = linea.split("=")[1].strip().strip("'") 
	elif linea.startswith("USER"):
		USER = linea.split("=")[1].strip().strip("'")
	elif linea.startswith("PASSWORD"):
		PASSWORD = linea.split("=")[1].strip().strip("'")
	elif linea.startswith("token"):
		TOKEN = linea.split("=")[1].strip().strip("'")
	elif linea.startswith("gist_id"):
		GIST_ID = linea.split("=")[1].strip().strip("'")



def enviarMensaje(mensaje):
	import requests
	"""
	# Abrir el archivo de texto en modo lectura
	with open("/home/villafapd/Documents/ConfigEspeciales/BotTelegram.txt", "r") as archivo:
		# Leer las líneas del archivo
		lineas = archivo.readlines()

	# Inicializar las variables
	idBot = ""
	idGrupo = ""
	idmio = ""

	# Procesar las lineas del archivo
	for linea in lineas:
		if linea.startswith("idBot"):
			idBot = linea.split("=")[1].strip().strip("'")
		elif linea.startswith("idGrupo"):
			idGrupo = linea.split("=")[1].strip().strip("'")
		elif linea.startswith("idmio"):
			idmio = linea.split("=")[1].strip().strip("'")
	"""
	url = f'https://api.telegram.org/bot{idBot}/sendMessage'
	requests.post(url, data={'chat_id': idmio, 'text': mensaje, 'parse_mode': 'HTML'})
	print("Mensaje de Respuesta Telegram vía url api")
 
"""
def enviarDocumento(ruta):
	import requests
	requests.post('https://api.telegram.org/bot' + idBot + '/sendDocument',
			  files={'document': (ruta, open(ruta, 'rb'))},
			  data={'chat_id': idGrupo, 'caption': 'imagen Oasys Norte'})
"""

def HoraFecha():
	#global hora, minutos, segundos, dia, mes, ano, microsegundos, diasemana, semanaano, milliseg
	
	ahora = datetime.now()#.time()
	date = datetime.now().today()
	hora_actual = ahora.strftime("%H:%M:%S")
	hora = ahora.hour
	hora = f"{hora:02d}"
	minutos = ahora.minute
	minutos = f"{minutos:02d}"
	segundos = ahora.second
	segundos = f"{segundos:02d}"
	dia = date.day
	dia = f"{dia:02d}"
	mes = date.month
	mes = f"{mes:02d}"
	ano = str(date.year)
	return hora, minutos, segundos, dia, mes, ano

def borrar_contenido_log(file_log):
	# Abrimos el archivo en modo 'w' para sobrescribirlo con un archivo vacio
	with open(file_log, 'w') as f:
		pass  # No es necesario escribir nada; simplemente abrimos y cerramos.

def reporte_url_Log(url_capturada, path_file_log):	
	f = open(path_file_log, 'a') # Abrimos nuestro fichero log en modo 'Añadir'. 
	f.write(" ".join([url_capturada, "\n"])) # Escribimos la linea de log en el fichero.
	f.close() # Cerramos el fichero para que se guarde. 

def buscar_url(archivo_log):
	# Leer el contenido del archivo
	with open(archivo_log, 'r') as file:
		log = file.read()    
	# Definir el patron de la URL
	patron = r"https://sae\d+\.playlist\.ttvnw\.net/v1/playlist/[A-Za-z0-9-_]+\.m3u8"    
	# Buscar todas las coincidencias del patr�n en el log
	urls = re.findall(patron, log)    
	return urls

def buscar_url9mza(archivo_log):
	# Leer el contenido del archivo
	with open(archivo_log, 'r') as file:
		log = file.read()    
	# Definir el patron de la URL
	patron = "https://unlimited\d+-saopaulo\.dps\.live/televidaar/televidaar\.smil/televidaar/livestream\d*/chunks\.m3u8\?nimblesessionid=\d+"
	# Buscar todas las coincidencias del patr�n en el log
	urls = re.findall(patron, log)    
	return urls

def buscar_urlnettv(archivo_log):
	# Leer el contenido del archivo
	with open(archivo_log, 'r') as file:
		log = file.read()    
	# Definir el patron de la URL
	# https://unlimited\d+-saopaulo\.dps\.live/nettv/nettv.smil/nettv/livestream1/chunks.m3u8?nimblesessionid=70311574
	patron = "https://unlimited\d+-saopaulo\.dps\.live/nettv/nettv\.smil/nettv/livestream\d*/chunks\.m3u8\?nimblesessionid=\d+"
	# Buscar todas las coincidencias del patr�n en el log
	urls = re.findall(patron, log)    
	return urls

def update_lista(Path_log_geckordp,linea,canal):	
	# Buscar las URLs en el archivo de log
	urls_encontradas = buscar_url(Path_log_geckordp)
	# Mostrar las URLs encontradas
	for url in urls_encontradas:
		hora, minutos, segundos, dia, mes, ano = HoraFecha()
		print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + url)
		# Abro el archivo de la lista de canales 
		data = open(Path_ListaTv_DomoCasa).read()
		# Dividimos el contenido en líneas
		lines = data.split('\n')
		# Comprobamos si hay al menos 27 líneas y actualizamos la línea 26
		if len(lines) >= 26:        
			lines[linea] = url # Actualizamos la línea
			updated_content = '\n'.join(lines)   
		try:
			with open(Path_ListaTv_DomoCasa, 'w') as archivo:
				archivo.writelines(updated_content)
			hora, minutos, segundos, dia, mes, ano = HoraFecha()
			print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + "Lista de canales actualizada y guardada correctamente.")
			enviarMensaje("Caputura url correctamente para canal: " + canal)
			break
		except Exception as e: # Captura excepciones más generales para un mejor manejo de errores
			print(f"Error al guardar el archivo: {e}")  
			enviarMensaje("Error al guardar el archivo: " + e + " -> Canal: " + canal)

def update_lista_mza(Path_log_geckordp,linea,canal):	
	# Buscar las URLs en el archivo de log
	urls_encontradas = buscar_url9mza(Path_log_geckordp)
	# Mostrar las URLs encontradas
	for url in urls_encontradas:
		hora, minutos, segundos, dia, mes, ano = HoraFecha()
		print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + url)
		# Abro el archivo de la lista de canales 
		data = open(Path_ListaTv_DomoCasa).read()
		# Dividimos el contenido en líneas
		lines = data.split('\n')
		# Comprobamos si hay al menos 27 líneas y actualizamos la línea 26
		if len(lines) >= 26:        
			lines[linea] = url # Actualizamos la línea
			updated_content = '\n'.join(lines)   
		try:
			with open(Path_ListaTv_DomoCasa, 'w') as archivo:
				archivo.writelines(updated_content)
			hora, minutos, segundos, dia, mes, ano = HoraFecha()
			print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + "Lista de canales actualizada y guardada correctamente.")
			enviarMensaje("Caputura url correctamente para canal: " + canal)

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
				f'https://api.github.com/gists/{GIST_ID}',
				headers={
					'Authorization': f'token {TOKEN}',
					'Content-Type': 'application/json; charset=utf-8'
				},
				data=json.dumps(update_data).encode('utf-8')
			)


		#'Authorization': f'token {token}'},
		#		data=json.dumps(update_data)
		#	)

			if response.status_code == 200:
				print("Gist actualizado exitosamente!")
			else:
				print("Error al actualizar el Gist:", response.status_code)

			break
		except Exception as e: # Captura excepciones más generales para un mejor manejo de errores
			print(f"Error al guardar el archivo: {e}")  
			enviarMensaje("Error al guardar el archivo: " + e + " -> Canal: " + canal)

def update_lista_nettv(Path_log_geckordp,linea,canal):	
	# Buscar las URLs en el archivo de log
	urls_encontradas = buscar_urlnettv(Path_log_geckordp)
	# Mostrar las URLs encontradas
	for url in urls_encontradas:
		hora, minutos, segundos, dia, mes, ano = HoraFecha()
		print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + url)
		# Abro el archivo de la lista de canales 
		data = open(Path_ListaTv_DomoCasa).read()
		# Dividimos el contenido en líneas
		lines = data.split('\n')
		# Comprobamos si hay al menos 27 líneas y actualizamos la línea 26
		if len(lines) >= 26:        
			lines[linea] = url # Actualizamos la línea
			updated_content = '\n'.join(lines)   
		try:
			with open(Path_ListaTv_DomoCasa, 'w') as archivo:
				archivo.writelines(updated_content)
			hora, minutos, segundos, dia, mes, ano = HoraFecha()
			print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "---> " + "Lista de canales actualizada y guardada correctamente.")
			enviarMensaje("Caputura url correctamente para canal: " + canal)

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
				f'https://api.github.com/gists/{GIST_ID}',
				headers={
					'Authorization': f'token {TOKEN}',
					'Content-Type': 'application/json; charset=utf-8'
				},
				data=json.dumps(update_data).encode('utf-8')
			)


		#'Authorization': f'token {token}'},
		#		data=json.dumps(update_data)
		#	)

			if response.status_code == 200:
				print("Gist actualizado exitosamente!")
			else:
				print("Error al actualizar el Gist:", response.status_code)

			break
		except Exception as e: # Captura excepciones más generales para un mejor manejo de errores
			print(f"Error al guardar el archivo: {e}")  
			enviarMensaje("Error al guardar el archivo: " + e + " -> Canal: " + canal)



def main(url,path_file):

	#GECKORDP.LOG_FILE = file #: enabled
	borrar_contenido_log(path_file)
	try:
		parser = argparse.ArgumentParser(description="")
		parser.add_argument(
			"--host", type=str, default="localhost", help="The host to connect to"
		)
		parser.add_argument(
			"--port", type=int, default="15200", help="The port to connect to"
		)
		args, _ = parser.parse_known_args()

		# clone default profile to 'geckordp'
		pm = ProfileManager()
		profile_name = "geckordp"
		pm.clone("default", profile_name)
		profile = pm.get_profile_by_name(profile_name)
		profile.set_required_configs()

		# start firefox with specified profile
		firefox_instance = Firefox.start(url, args.port, profile_name,  auto_kill=True,  wait=True) #["-headless"],
		time.sleep(45) #Raspberry ocupada en otros procesos
		# RDPClient
		###################################################
		client = RDPClient()
		client.connect(args.host, args.port)

		# RootActor
		###################################################
		ROOT = RootActor(client)
		root_actor_ids = ROOT.get_root()

		# DeviceActor
		###################################################
		DEVICE = DeviceActor(client, root_actor_ids["deviceActor"])

		# ContentProcessActor
		###################################################
		process_descriptors = ROOT.list_processes()
		for descriptor in process_descriptors:
			actor_id = descriptor["actor"]
			is_parent = descriptor["isParent"]

			PROCESS = ProcessActor(client, actor_id)
			target_ctx = PROCESS.get_target()

			CONSOLE = WebConsoleActor(client, target_ctx["consoleActor"])

			if not is_parent:
				CONTENT_PROCESS = ContentProcessActor(client, target_ctx["actor"])

		# WebExtensionActor
		###################################################
		for descriptor in ROOT.list_addons():
			EXTENSION = WebExtensionActor(client, descriptor["actor"])

		# WorkerActor
		###################################################
		for descriptor in ROOT.list_workers():
			WORKER = WorkerActor(client, descriptor["actor"])

		# AddonsActor
		###################################################
		ADDONS = AddonsActor(client, root_actor_ids["addonsActor"])

		# TabActor
		###################################################
		tab_ctx = ROOT.list_tabs()[0]
		TAB = TabActor(client, tab_ctx["actor"])
		actor_ids = TAB.get_target()

		# AccessibilityActor
		###################################################
		#ACCESSIBILITY = AccessibilityActor(client, actor_ids["accessibilityActor"])
		#ACCESSIBILITY.bootstrap()

		# ParentAccessibilityActor
		###################################################
		PARENT_ACCESSIBILITY = ParentAccessibilityActor(
			client, root_actor_ids["parentAccessibilityActor"]
		)
		PARENT_ACCESSIBILITY.bootstrap()
		PARENT_ACCESSIBILITY.enable()

		# AccessibleWalkerActor
		###################################################
		#ACCESSIBILITY_WALKER = AccessibleWalkerActor(
		#	client, ACCESSIBILITY.get_walker()["actor"]
		#)

		# AccessibleActor
		###################################################
		#accessible_children = ACCESSIBILITY_WALKER.children()
		#ACCESSIBLE = AccessibleActor(client, accessible_children[0]["actor"])

		# SimulatorActor
		###################################################
		#simulator = SimulatorActor(client, ACCESSIBILITY.get_simulator())

		# WindowGlobalActor
		###################################################
		WEB = WindowGlobalActor(client, actor_ids["actor"])

		# WebConsoleActor
		###################################################
		CONSOLE = WebConsoleActor(client, actor_ids["consoleActor"])
		CONSOLE.start_listeners([])

		# ThreadActor
		###################################################
		THREAD = ThreadActor(client, actor_ids["threadActor"])
		THREAD.attach()

		# WatcherActor
		###################################################
		watcher_ctx = TAB.get_watcher()
		WATCHER = WatcherActor(client, watcher_ctx["actor"])
		WATCHER.watch_resources(
			[
				Resources.NETWORK_EVENT,
				Resources.NETWORK_EVENT_STACKTRACE,
				Resources.DOCUMENT_EVENT,
			]
		)

		# NetworkParentActor
		###################################################
		#network_parent_ctx = WATCHER.get_network_parent_actor()
		#NETWORK_PARENT = NetworkParentActor(client, network_parent_ctx["network"]["actor"])

		# NetworkContentActor
		###################################################
		NETWORK_CONTENT = NetworkContentActor(client, actor_ids["networkContentActor"])

		# WebExtensionInspectedWindowActor
		###################################################
		WEB_EXT = WebExtensionInspectedWindowActor(
			client, actor_ids["webExtensionInspectedWindowActor"]
		)

		# InspectorActor
		###################################################
		INSPECTOR = InspectorActor(client, actor_ids["inspectorActor"])

		# WalkerActor
		###################################################
		walker_ctx = INSPECTOR.get_walker()
		WALKER = WalkerActor(client, walker_ctx["actor"])

		# NodeListActor
		###################################################
		document = WALKER.document()
		dom_node_list = WALKER.query_selector_all(document["actor"], "body h1")
		NODE_LIST = NodeListActor(client, dom_node_list["actor"])

		# NodeActor
		###################################################
		#node_element = WALKER.query_selector(document["actor"], "body h1")["node"]
		#NODE = NodeActor(client, node_element["actor"])

		# MemoryActor
		###################################################
		MEMORY = MemoryActor(client, actor_ids["memoryActor"])
		MEMORY.attach()

		# SourceActor
		###################################################
		#for descriptor in THREAD.sources():
		#	if descriptor.get("actor", None) is not None:
		#		SOURCE = SourceActor(client, descriptor["actor"])

		# HeapSnapshotActor
		###################################################
		SNAPSHOT = HeapSnapshotActor(client, root_actor_ids["heapSnapshotFileActor"])

		# PreferenceActor
		###################################################
		PERFERENCE = PreferenceActor(client, root_actor_ids["preferenceActor"])

		# TargetConfigurationActor
		###################################################
		target_config_ctx = WATCHER.get_target_configuration_actor()
		TARGET_CONFIG = TargetConfigurationActor(client, target_config_ctx["actor"])

		# ThreadConfigurationActor
		###################################################
		thread_config_ctx = WATCHER.get_thread_configuration_actor()
		THREAD_CONFIG = ThreadConfigurationActor(client, thread_config_ctx["actor"])

		# Get global target process
		###################################################
		global_target_ctx = {}
		target_fut = Future()

		async def on_target(data: dict):
			if "target" not in data or "browsingContextID" not in data["target"]:
				return
			if tab_ctx["browsingContextID"] == data["target"]["browsingContextID"]:
				target_fut.set_result(data["target"])

		client.add_event_listener(
			WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target
		)

		try:
			WATCHER.watch_targets(WatcherActor.Targets.FRAME)
			global_target_ctx = target_fut.result(3.0)
		finally:
			client.remove_event_listener(
				WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target
			)

		# CacheStorageActor
		###################################################
		cache_resource = {}
		cache_fut = Future()

		async def on_cache_resource(data: dict):
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "Cache" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							if "Cache" in obj.get("actor", ""):
								# just get the first one for example purposes
								try:
									cache_fut.set_result(obj)
								except:
									pass
								break

		client.add_event_listener(
			global_target_ctx["actor"],
			Events.Watcher.RESOURCES_AVAILABLE_ARRAY,
			on_cache_resource,
		)

		WATCHER.watch_resources([Resources.CACHE_STORAGE])

		cache_resource = cache_fut.result(3.0)

		cache_storage_id = cache_resource.get("actor", "")
		CACHE = CacheStorageActor(client, cache_storage_id)

		# CookieStorageActor
		###################################################
		cookie_resource = {}
		cookie_fut = Future()

		async def on_cookie_resource(data: dict):
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "cookies" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							if "cookie" in obj.get("actor", ""):
								# just get the first one for example purposes
								try:
									cookie_fut.set_result(obj)
								except:
									pass
								break

		client.add_event_listener(
			WATCHER.actor_id, Events.Watcher.RESOURCES_AVAILABLE_ARRAY, on_cookie_resource
		)

		WATCHER.watch_resources([Resources.COOKIE])

		cookie_resource = cookie_fut.result(3.0)

		cookie_storage_id = cookie_resource.get("actor", "")
		COOKIE = CookieStorageActor(client, cookie_storage_id)

		# ExtensionStorageActor
		###################################################
		""" At the moment not possible. 
		See also tests/actors/test_storage_extension. """
		# IndexedDBStorageActor
		###################################################
		indexed_resource = {}
		indexed_fut = Future()

		async def on_indexed_resource(data: dict):
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "indexed-db" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							if "indexedDB" in obj.get("actor", ""):
								# just get the first one for example purposes
								try:
									indexed_fut.set_result(obj)
								except:
									pass
								break

		client.add_event_listener(
			WATCHER.actor_id, Events.Watcher.RESOURCES_AVAILABLE_ARRAY, on_indexed_resource
		)

		WATCHER.watch_targets(WatcherActor.Targets.FRAME)
		WATCHER.watch_resources([Resources.INDEXED_DB])

		indexed_resource = indexed_fut.result(3.0)

		indexed_storage_id = indexed_resource.get("actor", "")
		INDEXED = IndexedDBStorageActor(client, indexed_storage_id)

		# LocalStorageActor
		###################################################
		local_resource = {}
		local_fut = Future()

		async def on_local_resource(data: dict):
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "local-storage" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							if "local" in obj.get("actor", ""):
								# just get the first one for example purposes
								try:
									local_fut.set_result(obj)
								except:
									pass
								break

		client.add_event_listener(
			global_target_ctx["actor"],
			Events.Watcher.RESOURCES_AVAILABLE_ARRAY,
			on_local_resource,
		)

		WATCHER.watch_resources([Resources.LOCAL_STORAGE])

		local_resource = local_fut.result(3.0)

		local_storage_id = local_resource.get("actor", "")
		LOCAL = LocalStorageActor(client, local_storage_id)

		# SessionStorageActor
		###################################################
		session_resource = {}
		session_fut = Future()

		async def on_session_resource(data: dict):
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "session-storage" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							if "session" in obj.get("actor", ""):
								# just get the first one for example purposes
								try:
									session_fut.set_result(obj)
								except:
									pass
								break

		client.add_event_listener(
			global_target_ctx["actor"],
			Events.Watcher.RESOURCES_AVAILABLE_ARRAY,
			on_session_resource,
		)

		WATCHER.watch_targets(WatcherActor.Targets.FRAME)
		WATCHER.watch_resources([Resources.SESSION_STORAGE])

		session_resource = session_fut.result(3.0)

		session_storage_id = session_resource.get("actor", "")
		SESSION = SessionStorageActor(client, session_storage_id)

		# ScreenshotActor
		###################################################
		SCREENSHOT = ScreenshotActor(client, root_actor_ids["screenshotActor"])

		# StringActor
		###################################################

		def on_evaluation_result(data: dict):
			"""
			- return a large enough string with 'evaluate_js_async()'
			to trigger a longString response from server
			"""
			result = data.get("result", data)
			if not isinstance(result, dict):
				return
			if result.get("type", "") != "longString":
				return
			STRING = StringActor(client, result["actor"])
			final_string_result = STRING.substring(0, result["length"])
			print(f"final_string_result(truncated): {final_string_result:5.5}...")

		client.add_event_listener(
			CONSOLE.actor_id, Events.WebConsole.EVALUATION_RESULT, on_evaluation_result
		)

		CONSOLE.evaluate_js_async(
			"""
			(() => { 
				longString = '';
				for (let i = 0; i < 10000; i++) {
					longString += 'x';
				}
				return longString; 
			})();
		"""
		)

		# NetworkEventActor
		###################################################

		def on_resource_available(data):
			"""
			the 'actor_id' here represents a connection to a specified url or resource
			after receiving it is possible to also receive updates for this ID with 'resource-updated-form'
			if a host is visited, multiple connections are be established each with its own 'actor_id'
			see also the network tab in the developer tools to see how it works
			"""
			array = data.get("array", [])
			for sub_array in array:
				sub_array: list
				for i, item in enumerate(sub_array):
					item: str | list
					if isinstance(item, str) and "network-event" in item:
						# obj[i + 1] = next item in array
						for obj in sub_array[i + 1]:
							obj: dict
							actor_id = obj.get("actor", "")
							resource_id = obj.get("resourceId", -1)
							url = obj.get("url", "N/A")
							reporte_url_Log(url, path_file)
							if "netEvent" in actor_id and resource_id != -1:
								NETWORK_EVENT = NetworkEventActor(client, actor_id)
								request = NETWORK_EVENT.get_request_headers()
								print(
									f"request headers:\n{json.dumps(request['headers'], indent=2)}"
								)

		""" 
		- register handler and trigger it by visiting a new page
		- received actor IDs can be also stored temporary
		and initiated later
		"""
		client.add_event_listener(
			watcher_ctx["actor"],
			Events.Watcher.RESOURCES_AVAILABLE_ARRAY,
			on_resource_available,
		)
		time.sleep(25)
		#input()
		client.disconnect()
		client.remove_event_listener(WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target)
		client.remove_actor_listener(WATCHER.actor_id, on_target)
		firefox_instance.kill()
	
	except Exception as e:
		print(str(e), "Reincio")
		client.disconnect()
		#client.remove_event_listener(WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target)
		#client.remove_actor_listener(WATCHER.actor_id, on_target)
		firefox_instance.kill()
		enviarMensaje("Error en ejecución de función main: " + str(e) )
		#exit()	
	
  


if __name__ == "__main__":
	
# Programar la funcion para que se ejecute cada 12 horas
#link canal original https://www.twitch.tv/elnueveok
#link canal original https://www.twitch.tv/canalshowsport
	schedule.every().day.at("00:10").do(partial(main,"moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=elnueveenvivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log"))
	schedule.every().day.at("00:12").do(partial(main,"moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=canalshowsport","/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log"))
	schedule.every().day.at("00:13").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log",20,"El Nueve"))
	schedule.every().day.at("00:14").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log",53, "ShowSports"))
	

	schedule.every().day.at("08:10").do(partial(main,"moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=elnueveenvivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log"))
	schedule.every().day.at("08:12").do(partial(main,"moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=canalshowsport","/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log"))
	schedule.every().day.at("08:13").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log",20, "El Nueve"))
	schedule.every().day.at("08:14").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log",53, "ShowSports"))


	schedule.every().day.at("16:10").do(partial(main,"https://www.elnueve.com.ar/en-vivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log"))
	schedule.every().day.at("16:12").do(partial(main,"moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=canalshowsport","/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log"))
	schedule.every().day.at("16:13").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log",20, "El Nueve"))
	schedule.every().day.at("16:14").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log",53, "ShowSports"))
	#schedule.every().day.at("16:15").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve_mza.log",2, "El Nueve Mza"))


	#Se ejecuta al minuto 48 de cada hora
	schedule.every().hour.at(":48").do(partial(main, "https://www.canalnet.tv/page/senal-en-vivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_nettv.log"))
 	#Se ejecuta al minuto 50 de cada hora
	schedule.every().hour.at(":50").do(partial(update_lista_nettv,"/home/villafapd/Documents/PythonProjects/Elnueve/url_nettv.log",26, "Net Tv"))
	#Se ejecuta al minuto 50 de cada hora
	schedule.every().hour.at(":50").do(partial(main, "https://www.elnueve.com/page/en-vivo/","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve_mza.log"))
 	#Se ejecuta al minuto 52 de cada hora
	schedule.every().hour.at(":52").do(partial(update_lista_mza,"/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve_mza.log",2, "El_Nueve_Mza"))

    # Se ejecuta cada 10 segundos
	#schedule.every(10).seconds.do(partial(update_lista, "/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log", 53, "ShowSports"))
		

	# Para cambiar la frecuencia a 8 horas, puedes actualizar la programacion
	# schedule.clear()  # Limpia la programacion actual
	# schedule.every(8).hours.do(mi_funcion)
	
	hora, minutos, segundos, dia, mes, ano = HoraFecha()
	print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "--> " + "Escaneando Canal NetTV")
	main("https://www.canalnet.tv/page/senal-en-vivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_nettv.log")
	update_lista_nettv("/home/villafapd/Documents/PythonProjects/Elnueve/url_nettv.log",26, "NetTv")
	time.sleep(5)
	
	hora, minutos, segundos, dia, mes, ano = HoraFecha()
	print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "--> " + "Escaneando Canal El Nueve de Mendoza")
	main("https://www.elnueve.com/page/en-vivo/","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve_mza.log")
	update_lista_mza("/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve_mza.log",2, "El Nueve mza")
	
	time.sleep(5)
	#https://www.elnueve.com.ar/en-vivo
	#moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=elnueveenvivo
	print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "--> " + "Escaneando Canal El Nueve de Buenos Aires")
	main("moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=elnueveenvivo","/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log")
	update_lista("/home/villafapd/Documents/PythonProjects/Elnueve/url_elnueve.log",20, "El Nueve")
	time.sleep(5)
	hora, minutos, segundos, dia, mes, ano = HoraFecha()
	print("Hora:" + hora + ":" + minutos + ":" + segundos + "--->" + "Fecha:" + dia + "-" + mes+ "-" + ano + "--> " + "Escaneando Canal Show Sports")
	main("moz-extension://b06a910a-a14a-4f77-a09c-7a2a8c77e414/player.html?channel=canalshowsport","/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log")
	update_lista("/home/villafapd/Documents/PythonProjects/Elnueve/url_showsports.log",53, "ShowSports")
	




	try:
		
		while True:
			schedule.run_pending()
			time.sleep(5)
	except KeyboardInterrupt:
		print("Programa interrumpido. Limpiando recursos...") 
 
