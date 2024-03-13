console.log("Enviando peticion")

fetch("http://127.0.0.1:3333/api/publicacion")
    .then((res) => res.json())
    .then((data) => {
        console.log(data)
    })
    .catch((err) => {
        console.log(err)
    })