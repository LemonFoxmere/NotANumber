import anime from 'animejs';
import { callbacks, sleep } from "./app";

// start putting html of pixels in
for(let i = 0; i < 28; i++){
    for(let j = 0; j < 28; j++){
        let pixel = document.createElement("div")
        pixel.classList.add("img-pixel")
        pixel.id=`${i}/${j}`
        document.getElementById("pixel-display")!.appendChild(pixel)
    }
}

export let set_image = (image_data: number[]) => {
    return new Promise((res: callbacks, rej: callbacks): void => {
        // go through every pixel and set them correspondingly
        let pixel_ct: number = 0
        for(let i = 0; i < 28; i++){
            for(let j = 0; j < 28; j++){
                document.getElementById(`${i}/${j}`)!.style.opacity = String(image_data[++pixel_ct]/255)
            }
        }
        res()
    })
}

// add event listener to all the card returns
document.querySelectorAll(".close-card").forEach(e => {
    e.addEventListener("mouseup", () => {
        e.parentElement!.classList.add("notransition")
        anime({
            targets: e.parentElement,
            translateY: {
                value: "-7rem",
                easing:"easeInBack",
                duration: 400,
            },
            opacity:{
                value:0,
                easing:"linear",
                duration: 200,
            },
            complete: () => {
                e.parentElement!.classList.add("disable-hidden")
                document.getElementById("clicker-blocker")!.classList.add("disable-hidden")  // enable background clicking
            }
        })
    })
})

let summon_card = (card_id: string) => {
    let e = document.getElementById(card_id)
    if(e) e.classList.remove("disable-hidden")
    document.getElementById("clicker-blocker")!.classList.remove("disable-hidden") // disable background clicking
    anime({
        targets: e,
        translateY: {
            value: "0rem",
            easing:"easeOutElastic",
            duration: 900,
        },
        opacity:{
            value: 1,
            easing:"linear",
            duration: 200,
        },
        delay: 100,
        complete: () => {
            if(e) e.classList.remove("notransition")
        }
    })
}

// open menu
let mobile_menu = {
    menu_hidden: true,
    toggle: function (){
        this.set(this.menu_hidden)
        this.menu_hidden = !this.menu_hidden
    },

    set: async function (shown:boolean, transition:boolean = true){
        if(!transition){ //disable transition for both elements
            document.getElementById("menu-open-btn")!.classList.add("notransition");
            document.getElementById("nav-content")!.classList.add("notransition");
        }

        if(shown){ // if true, revert to false. This shows the mobile menu
            document.getElementById("menu-open-btn")!.classList.add("btn-menu-hidden");
            document.getElementById("nav-content")!.classList.remove("menu-hidden");
            document.getElementById("main-nav")!.classList.add("mobile-nav");
        } else { // this hides the mobile menu
            document.getElementById("menu-open-btn")!.classList.remove("btn-menu-hidden") // if false, revert to true
            document.getElementById("nav-content")!.classList.add("menu-hidden")
            document.getElementById("main-nav")!.classList.remove("mobile-nav")
        }

        setTimeout(():void => {
            document.getElementById("menu-open-btn")!.classList.remove("notransition")
            document.getElementById("nav-content")!.classList.remove("notransition")
        }, 20)
    }
}

// add button event listners
document.getElementById("menu-open-btn")!.addEventListener("click", (e):void => {
    mobile_menu.toggle() // toggle mobile menu on and off
});
document.getElementById("about-nav-btn")!.addEventListener("click", (e):void => {
    summon_card('abt-card') // toggle about card on and off
}); document.getElementById("nav-logo")!.addEventListener("click", (e):void => {
    summon_card('abt-card') // toggle about card on and off
});

// on window resize, add menu hide
window.onresize = win => {
    if(window.innerWidth > 900){
        mobile_menu.set(true, false)
    } else if (mobile_menu.menu_hidden){
        mobile_menu.set(false, false)
    }
}
window.onload = () => { // set visibility based on device on first startup
    if(window.innerWidth > 900){
        mobile_menu.set(true, false)
    } else if (mobile_menu.menu_hidden){
        mobile_menu.set(false, false)
    }
}