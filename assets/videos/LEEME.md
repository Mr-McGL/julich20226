# Vídeos del PowerPoint

El original contiene cinco objetos de vídeo, pero sus ficheros no están incrustados. Se conservan los pósteres y las referencias. No hay archivos de vídeo reproducibles en esta carpeta.

| Diapositiva | Objeto original | Ruta esperada |
| --- | --- | --- |
| 7 | videoplayback | `slide-07-1158545669.mp4` |
| 11 | SnapSave.io-MeLVin(360p) | `slide-11-2066184930.mp4` |
| 13 | DSNet2 | `slide-13-1419470627.mp4` |
| 13 | DSNet3 | `slide-13-955489805.mp4` |
| 21 | cl04_32_33_espina_manipulate_facet | `slide-21-516877989.mp4` |

Copia los vídeos recuperados a esta carpeta con esos nombres. No necesitas editar el CSS: las posiciones dependen del diseño y del orden multimedia, no del nombre del fichero.

Para incorporar un MP4 o WebM con otro nombre, ejecuta desde la raíz del proyecto:

```bash
python scripts/attach_video.py --slide 7 --file /path/to/video.mp4
python scripts/attach_video.py --slide 13 --shape-id 1419470627 --file /path/to/video.webm
```

El script cambia únicamente el atributo `src` del objeto elegido y actualiza el inventario; mantiene el póster, los controles y el diseño. Guarda una copia de seguridad de `presentacion.md`. Regenera después los HTML exportados.

Los registros de `missing-videos.json` conservan las relaciones y los identificadores originales del PowerPoint. El campo `html_class` es histórico: no se utiliza para colocar los vídeos en la versión actual.
