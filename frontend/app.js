function consulta_general() {
    let url = "http://127.0.0.1:5000/";
    fetch(url)
        .then(response => response.json())
        .then(data => visualizar(data))
        .catch(error => console.log(error));

    const visualizar = (data) => {
        console.log(data);
        let b = "";
        for (var i = 0; i < data.baul.length; i++) {
            b += `<tr><td>${data.baul[i].id_baul}</td>
                  <td>${data.baul[i].Plataforma}</td>
                  <td>${data.baul[i].usuario}</td>
                  <td>${data.baul[i].clave}</td>
                  <td><button type='button' class='btn btn-info' onclick="location.href='edit.html?variable1=${data.baul[i].id_baul}'">
                  <img src='img/edit.svg' height='30' width='30'/></button>
                  <button type='button' class='btn btn-warning' onclick="eliminar(${data.baul[i].id_baul})">
                  <img src='img/delete.png' height='30' width='30'/></button></td></tr>`;
        }
        document.getElementById('data').innerHTML = b;
    };
}

function eliminar(id) {
    let url = `http://127.0.0.1:5000/eliminar/${id}`;
    fetch(url, { method: 'DELETE' })
        .then(response => response.json())
        .then(res => {
            swal("Mensaje", "Registro " + res.mensaje + " exitosamente", "success")
                .then(() => window.location.reload());
        });
}

function registrar() {
    let url = "http://127.0.0.1:5000/registro/";
    let plat = document.getElementById("plataforma").value;
    let usua = document.getElementById("usuario").value;
    let clav = document.getElementById("clave").value;
    let data = { "plataforma": plat, "usuario": usua, "clave": clav };

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            if (response.mensaje == "Error") {
                swal("Mensaje", "Hubo un error", "error");
            } else {
                swal("Mensaje", "Registro agregado correctamente", "success")
                    .then(() => {
                        location.href = 'index.html';
                    });
            }
        })
        .catch(error => console.log("Error en la solicitud:", error));
}


function modificar(id) {
    let url = `http://127.0.0.1:5000/actualizar/${id}`;
    let plat = document.getElementById("plataforma").value;
    let usua = document.getElementById("usuario").value;
    let clav = document.getElementById("clave").value;
    let data = { "plataforma": plat, "usuario": usua, "clave": clav };

    fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
        .then(res => res.json())
        .then(response => {
            swal("Mensaje", "Registro actualizado exitosamente", "success");
        });
}
