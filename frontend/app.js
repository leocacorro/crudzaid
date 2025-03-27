function consulta_general() {
    let url = "http://127.0.0.1:5000/";  // URL del endpoint para obtener todos los registros
    fetch(url)  // Realizando una solicitud GET a la URL
        .then(response => response.json())  // Convierte la respuesta a formato JSON
        .then(data => visualizar(data))  // Llama a la función visualizar con los datos obtenidos
        .catch(error => console.log(error));  // Manejo de errores en caso de fallo en la solicitud

    const visualizar = (data) => {  // Función para visualizar los datos en la tabla
        console.log(data);  // Imprimiendo los datos en la consola
        let b = "";  // Inicializando una variable para almacenar el HTML de la tabla
        for (var i = 0; i < data.baul.length; i++) {  // Iterando sobre cada registro
            b += `<tr><td>${data.baul[i].id_baul}</td>
                  <td>${data.baul[i].Plataforma}</td>
                  <td>${data.baul[i].usuario}</td>
                  <td>${data.baul[i].clave}</td>
                  <td><button type='button' class='btn btn-info' onclick="location.href='edit.html?variable1=${data.baul[i].id_baul}'">
                  <img src='img/edit.svg' height='30' width='30'/></button>
                  <button type='button' class='btn btn-warning' onclick="eliminar(${data.baul[i].id_baul})">
                  <img src='img/delete.png' height='30' width='30'/></button></td></tr>`;  // Creando filas de la tabla con botones para editar y eliminar
        }
        document.getElementById('data').innerHTML = b;  // Insertando el HTML generado en el elemento con id 'data'
    };
}

function eliminar(id) {
    let url = `http://127.0.0.1:5000/eliminar/${id}`;  // URL del endpoint para eliminar un registro específico
    fetch(url, { method: 'DELETE' })  // Realizando una solicitud DELETE a la URL
        .then(response => response.json())  // Convierte la respuesta a formato JSON
        .then(res => {
            swal("Mensaje", "Registro " + res.mensaje + " exitosamente", "success")  // Muestra un mensaje de éxito
                .then(() => window.location.reload());  // Recarga la página después de cerrar el mensaje
        });
}

function registrar() {
    let url = "http://127.0.0.1:5000/registro/";  // URL del endpoint para registrar un nuevo usuario
    let plat = document.getElementById("plataforma").value;  // Obteniendo el valor de la plataforma
    let usua = document.getElementById("usuario").value;  // Obteniendo el valor del usuario
    let clav = document.getElementById("clave").value;  // Obteniendo el valor de la contraseña
    let data = { "plataforma": plat, "usuario": usua, "clave": clav };  // Creando un objeto con los datos

    fetch(url, {
        method: "POST",  // Realizando una solicitud POST
        headers: { "Content-Type": "application/json" },  // Estableciendo el tipo de contenido
        body: JSON.stringify(data)  // Enviando los datos como JSON
    })
        .then(res => res.json())  // Convierte la respuesta a formato JSON
        .then(response => {
            if (response.mensaje == "Error") {  // Verificando si hubo un error
                swal("Mensaje", "Hubo un error", "error");  // Muestra un mensaje de error
            } else {
                swal("Mensaje", "Registro agregado correctamente", "success")  // Muestra un mensaje de éxito
                    .then(() => {
                        location.href = 'index.html';  // Redirige a la página principal
                    });
            }
        })
        .catch(error => console.log("Error en la solicitud:", error));  // Manejo de errores en caso de fallo en la solicitud
}

function modificar(id) {
    let url = `http://127.0.0.1:5000/actualizar/${id}`;  // URL del endpoint para actualizar un registro específico
    let plat = document.getElementById("plataforma").value;  // Obteniendo el valor de la plataforma
    let usua = document.getElementById("usuario").value;  // Obteniendo el valor del usuario
    let clav = document.getElementById("clave").value;  // Obteniendo el valor de la contraseña
    let data = { "plataforma": plat, "usuario": usua, "clave": clav };  // Creando un objeto con los datos

    fetch(url, {
        method: "PUT",  // Realizando una solicitud PUT
        headers: { "Content-Type": "application/json" },  // Estableciendo el tipo de contenido
        body: JSON.stringify(data)  // Enviando los datos como JSON
    })
        .then(res => res.json())  // Convierte la respuesta a formato JSON
        .then(response => {
            swal("Mensaje", "Registro actualizado exitosamente", "success");  // Muestra un mensaje de éxito
        });
}
