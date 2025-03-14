
import argparse
import json
from concurrent.futures import Future
from geckordp.actors.accessibility.parent_accessibility import ParentAccessibilityActor
from geckordp.actors.addon.web_extension_inspected_window import (WebExtensionInspectedWindowActor,)
from geckordp.actors.descriptors.process import ProcessActor
from geckordp.actors.descriptors.tab import TabActor
from geckordp.actors.device import DeviceActor
from geckordp.actors.events import Events
from geckordp.actors.inspector import InspectorActor
from geckordp.actors.network_content import NetworkContentActor
from geckordp.actors.network_event import NetworkEventActor
from geckordp.actors.resources import Resources
from geckordp.actors.root import RootActor
from geckordp.actors.target_configuration import TargetConfigurationActor
from geckordp.actors.targets.window_global import WindowGlobalActor
from geckordp.actors.thread import ThreadActor
from geckordp.actors.thread_configuration import ThreadConfigurationActor
from geckordp.actors.watcher import WatcherActor
from geckordp.actors.web_console import WebConsoleActor
from geckordp.firefox import Firefox
from geckordp.profile import ProfileManager
from geckordp.rdp_client import RDPClient
import schedule
import time
import re
from functools import partial
from geckordp.settings import GECKORDP
import setproctitle

setproctitle.setproctitle("ScanTwichTv")
Path_ListaTv_DomoCasa = "/home/villafapd/Documents/PythonProjects/MiCasaDomo/ListaTv/listaCanaleslocal.m3u" 

def buscar_url(archivo_log):
	# Leer el contenido del archivo
	with open(archivo_log, 'r') as file:
		log = file.read()    
	# Definir el patron de la URL
	patron = r"https://sae\d+\.playlist\.ttvnw\.net/v1/playlist/[A-Za-z0-9-_]+\.m3u8"    
	# Buscar todas las coincidencias del patr�n en el log
	urls = re.findall(patron, log)    
	return urls


def update_lista(Path_log_geckordp,linea):	
	# Buscar las URLs en el archivo de log
	urls_encontradas = buscar_url(Path_log_geckordp)
	# Mostrar las URLs encontradas
	for url in urls_encontradas:
		print(url)
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
			print("Lista de canales actualizada y guardada correctamente.")
			
			break
		except Exception as e: # Captura excepciones más generales para un mejor manejo de errores
			print(f"Error al guardar el archivo: {e}")  

def main(url,file):
	GECKORDP.DEBUG = 1
	GECKORDP.DEBUG_REQUEST = 1
	GECKORDP.DEBUG_RESPONSE = 1
	GECKORDP.LOG_FILE = file #: enabled
    
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
		firefox_instance = Firefox.start(url, args.port, profile_name, auto_kill=True, wait=True) #["-headless"],
		time.sleep(30)
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


		# TabActor
		###################################################
		tab_ctx = ROOT.list_tabs()[0]
		TAB = TabActor(client, tab_ctx["actor"])
		actor_ids = TAB.get_target()


		# ParentAccessibilityActor
		###################################################
		PARENT_ACCESSIBILITY = ParentAccessibilityActor(client, root_actor_ids["parentAccessibilityActor"])
		PARENT_ACCESSIBILITY.bootstrap()
		PARENT_ACCESSIBILITY.enable()

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
			#global_target_ctx = target_fut.result(3.0)
		finally:
			client.remove_event_listener(
				WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target
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


		time.sleep(10)
		#input()
		client.disconnect()
		client.remove_event_listener(WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target)
		client.remove_actor_listener(WATCHER.actor_id, on_target)
		firefox_instance.kill()
	
	except Exception as e:
		print(e, "Reincio")
		client.disconnect()
		client.remove_event_listener(WATCHER.actor_id, Events.Watcher.TARGET_AVAILABLE_FORM, on_target)
		client.remove_actor_listener(WATCHER.actor_id, on_target)
		firefox_instance.kill()
		exit()	
	
  


if __name__ == "__main__":
	
# Programar la funcion para que se ejecute cada 6 horas
	schedule.every().day.at("07:00").do(partial(main,"https://www.twitch.tv/elnueveok","elnueve.log"))
	schedule.every().day.at("07:02").do(partial(main,"https://canalshowsport.com.ar/","showsports.log"))
	schedule.every().day.at("07:05").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/elnueve.log",20))
	schedule.every().day.at("07:05").do(partial(update_lista,"/home/villafapd/Documents/PythonProjects/Elnueve/showsports.log",53))
# Para cambiar la frecuencia a 8 horas, puedes actualizar la programacion
# schedule.clear()  # Limpia la programacion actual
# schedule.every(8).hours.do(mi_funcion)
	print("Escaneando El Nueve")
	main("https://www.twitch.tv/elnueveok","elnueve.log")
	time.sleep(5)
	print("Escaneand Show Sports")
	main("https://www.twitch.tv/canalshowsport","showsports.log")
	update_lista("/home/villafapd/Documents/PythonProjects/Elnueve/elnueve.log",20)
	update_lista("/home/villafapd/Documents/PythonProjects/Elnueve/showsports.log",53)
	try:
		while True:
			schedule.run_pending()
			time.sleep(5)
	except KeyboardInterrupt:
		print("Programa interrumpido. Limpiando recursos...") 
 
