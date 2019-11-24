function codeAddress() {
    document.body.className = "bat403";
    menu = document.getElementById("menu");
    menu.style.backgroundColor = "black";
    menu.style.color = "yellow"

    var array = Array.from(menu.children);
    array.forEach(item=> {item.children[0].style.color = "yellow";})    
    // for(ulItem  of menu.childNodes)
    // {
    //     ulItem.style.color = "yellow"        
    // }
    document.getElementById("hlavicka").style.backgroundColor = "black";
}
window.onload = codeAddress;