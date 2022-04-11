import { set_image } from "./loadUI"
import { openDB } from "idb"
import { latentoutput } from "./app"

export let start_listening_input = () => {
    // create image change promise

    const dbName:string = "ganout-db"
    const input_box = document.getElementById("input-box")
    if(!input_box) return "DOM failed to load"

    const dbPromise = openDB(dbName, 1, {
        upgrade(db, oldVersion, newVersion, transaction): any {
            if (!db.objectStoreNames.contains('latentout')) {
                return "Latent DB does not exist! Cannot load image."
            }
        },
    })

    dbPromise.then(db => { // open the db
        input_box.addEventListener("mousemove", async e => {
            try {
                await set_image(latentoutput[Math.floor(e.offsetX/input_box.clientWidth*200)][Math.floor(e.offsetY/input_box.clientHeight*200)]) // load image
            } catch (error) {
                console.warn("chunk failed to load.")
            }
        })

        input_box.addEventListener("touchmove", async e => {
            e.preventDefault()
            document.getElementById("mobile-guide")!.classList.add("disable-hidden")
            try {
                await set_image(latentoutput
                [Math.floor((e.touches[0].clientX - input_box.getBoundingClientRect().x)/input_box.getBoundingClientRect().width*200)]
                [Math.floor((e.touches[0].clientY - input_box.getBoundingClientRect().y)/input_box.getBoundingClientRect().height*200)]) // load image
            } catch (error) {
                console.warn("chunk failed to load.")
            }
        })
    })
}