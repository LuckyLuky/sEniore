function OnLoad() {
    let navItemList = document.getElementsByClassName("nav-item");
    for(i=0;i<navItemList.length;i++)
    {
        let hrefElement = navItemList[i].children[0]
        if(window.location.href == hrefElement.href)
        {
            hrefElement.classList.remove("nav-link");
            hrefElement.classList.add("active");
        }
        else
        {
            hrefElement.classList.remove("active");
            hrefElement.classList.add("nav-link");
        }

    }


}

window.onload = OnLoad;