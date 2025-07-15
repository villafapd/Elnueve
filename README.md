Simple ejemplo para capturar url de canales de tv

Usando geckordp se puede obtener la url de twich y llevarla a un reproductor de iptv
Se requiere de Firefox V 135 (ARM64) (no funciona en Chrome y Edge)
Se requiere addons "Alternate player for twichtv" link:https://addons.mozilla.org/en-US/firefox/addon/twitch_5/
Se usa "Alternate player for twichtv" porque es mas liviano para raspberry pi 4 y ademas no requiere loggin de twich para ciertos canales
Se debe configurar en firefox ---> about:config
  	media.geckoview.autoplay.request = True
Para Carga del addons con el canal se debe usar el identificador unico del addons "Alternate Player for Twich"
 	about:debugging#/runtime/this-firefox
	buscar "Internal UUID" en este caso "b06a910a-a14a-4f77-a09c-7a2a8c77e414" para mi navegador
Se envian notificaciones a telegram 

Canales a scanear con la aplicación
link canal original https://www.twitch.tv/elnueveok
link canal original https://www.twitch.tv/canalshowsport
link canal original https://www.elnueve.com/page/en-vivo/
