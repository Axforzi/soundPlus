# SoundPlus

<p align="center">
  <img src="myapp/static/img/logo.png" alt="Logo de SoundPlus" style="height: 100px">
</p>

SoundPlus es una aplicación web de música en línea desarrollada con Django inspirada en spotify. Permite a los usuarios buscar, reproducir y gestionar su música favorita de manera fácil y intuitiva.

<h2>Características</h2>

*   Búsqueda de música por artista, álbum, canción y lista de reproducción
*   Reproducción de música en línea con soporte para múltiples formatos de archivo
*   Creación y gestión de listas de reproducción personalizadas
*   Perfil de usuario con información de seguimiento y recomendaciones de música
*   Integración con redes sociales para compartir música y conectarse con otros usuarios

<h2>Tecnologías utilizadas</h2>

*   Django 3.x como framework de desarrollo web
*   Python 3.x como lenguaje de programación
*   HTML5, CSS3 y JavaScript para la interfaz de usuario
*   Base de datos relacional con SQLite
*   Servidor de desarrollo con Gunicorn

<h2>Instalación y configuración</h2>

<ol>
  <li>Clona el repositorio de GitHub: <code>git clone https://github.com/Axforzi/soundPlus.git</code></li>

  <li>Crea un entorno virtual con Python 3.x: <code>python3 -m venv env</code></li>

  <li>Activa el entorno virtual: <code>source env/bin/activate</code> (en Linux/Mac) o <code>env\Scripts\activate</code> (en Windows)</li>

  <li>Instala las dependencias de Django: <code>pip install -r requirements.txt</code></li>

  <li>Configura la variable de entorno <code>SECRET_KEY</code> con una clave secreta alfanumérica aleatoria de al menos 50 caracteres
  </li>

  <li>Configura la variable de entorno <code>DEBUG</code> como <code>True</code> o <code>False</code> para activar o desactivar el modo de depuración
  </li>

  <li>Configura la variable de entorno <code>CSRF_TRUSTED_ORIGINS</code> con los dominios confiables que pueden enviar solicitudes a la aplicación, separados por comas.
  </li>

  <li>Inicia el servidor de desarrollo: <code>python manage.py runserver</code></li>
</ol>

<h2>Uso</h2>

<ol>
  <li>Accede a la aplicación en <code>http://localhost:8000</code></li>
  <li>Registra un nuevo usuario o inicia sesión con un usuario existente</li>
  <li>Busca música y reproduce tus canciones favoritas</li>
  <li>Crea y gestiona tus listas de reproducción personalizadas</li>
</ol>

<h2>Contribuciones</h2>

SoundPlus es un proyecto de código abierto y cualquier contribución es bienvenida. Si deseas reportar un error o sugerir una nueva característica, por favor crea un issue en el repositorio de GitHub.

<h2> Descargo de responsabilidad </h2>

Este proyecto, SoundPlus, es una aplicación de música en línea desarrollada como ejercicio académico y no está afiliada, patrocinada ni respaldada por Spotify o sus socios.Todos los nombres, logotipos y marcas registradas mencionados pertenecen a sus respectivos dueños.

<h2>Licencia</h2>

SoundPlus está licenciado bajo la licencia MIT. Ver <code>LICENSE</code> para más información.

