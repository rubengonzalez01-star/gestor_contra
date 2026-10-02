const API = "http://127.0.0.1:5000/baul";

function obtenerTabla() {
    return document.getElementById("tabla-registros") || document.getElementById("data");
}

async function consulta_general() {
    const tabla = obtenerTabla();

    if (!tabla) {
        return;
    }

    try {
        const respuesta = await fetch(API);

        if (!respuesta.ok) {
            throw new Error("No se pudo obtener la lista");
        }

        const registros = await respuesta.json();
        const lista = Array.isArray(registros) ? registros : registros.baul || [];

        tabla.innerHTML = "";

        lista.forEach((registro) => {
            tabla.innerHTML += `
                <tr>
                    <td>${registro.id_baul}</td>
                    <td>${registro.Plataforma}</td>
                    <td>${registro.usuario}</td>
                    <td>${registro.clave}</td>
                    <td>
                        <a class="btn btn-primary btn-sm" href="edit.html?variable1=${registro.id_baul}">
                            Editar
                        </a>
                    </td>
                    <td>
                        <button class="btn btn-danger btn-sm" onclick="eliminar(${registro.id_baul})">
                            Eliminar
                        </button>
                    </td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Error al cargar los registros:", error);
    }
}

async function registrar() {
    const plataforma = document.getElementById("plataforma")?.value.trim();
    const usuario = document.getElementById("usuario")?.value.trim();
    const clave = document.getElementById("clave")?.value.trim();

    if (!plataforma || !usuario || !clave) {
        alert("Completa todos los campos");
        return;
    }

    try {
        const respuesta = await fetch(API, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                plataforma,
                usuario,
                clave
            })
        });

        const resultado = await respuesta.json();
        alert(resultado.mensaje || "Registro agregado");

        if (respuesta.ok) {
            window.location.href = "index.html";
        }
    } catch (error) {
        console.error("Error al registrar:", error);
        alert("Error al registrar");
    }
}

async function consulta_individual(id) {
    if (!id) {
        return;
    }

    try {
        const respuesta = await fetch(`${API}/${id}`);

        if (!respuesta.ok) {
            throw new Error("Registro no encontrado");
        }

        const registro = await respuesta.json();

        const plataformaInput = document.getElementById("plataforma");
        const usuarioInput = document.getElementById("usuario");
        const claveInput = document.getElementById("clave");

        if (plataformaInput) plataformaInput.value = registro.Plataforma;
        if (usuarioInput) usuarioInput.value = registro.usuario;
        if (claveInput) claveInput.value = registro.clave;
    } catch (error) {
        console.error("Error al consultar registro:", error);
    }
}

async function modificar(id) {
    const plataforma = document.getElementById("plataforma")?.value.trim();
    const usuario = document.getElementById("usuario")?.value.trim();
    const clave = document.getElementById("clave")?.value.trim();

    if (!id || !plataforma || !usuario || !clave) {
        alert("Completa todos los campos");
        return;
    }

    try {
        const respuesta = await fetch(`${API}/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                plataforma,
                usuario,
                clave
            })
        });

        const resultado = await respuesta.json();
        alert(resultado.mensaje || "Registro actualizado");

        if (respuesta.ok) {
            window.location.href = "index.html";
        }
    } catch (error) {
        console.error("Error al actualizar:", error);
        alert("Error al actualizar");
    }
}

async function eliminar(id) {
    const confirmar = confirm("¿Deseas eliminar este registro?");

    if (!confirmar) return;

    try {
        const respuesta = await fetch(`${API}/${id}`, {
            method: "DELETE"
        });

        const resultado = await respuesta.json();
        alert(resultado.mensaje || "Eliminado");

        if (respuesta.ok) {
            consulta_general();
        }
    } catch (error) {
        console.error("Error al eliminar:", error);
        alert("Error al eliminar");
    }
}

const formularioAgregar = document.getElementById("form-agregar");
if (formularioAgregar) {
    formularioAgregar.addEventListener("submit", async function (event) {
        event.preventDefault();
        await registrar();
    });
}

const formularioEditar = document.getElementById("form-editar");
if (formularioEditar) {
    const parametros = new URLSearchParams(window.location.search);
    const id = parametros.get("id") || parametros.get("variable1");

    if (id) {
        consulta_individual(id);
    }

    formularioEditar.addEventListener("submit", async function (event) {
        event.preventDefault();
        await modificar(id);
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", consulta_general);
} else {
    consulta_general();
}