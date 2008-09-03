// allow IE to recognize HTMl5 elements
if (!document.createElementNS) {
    document.createElement('section');
    document.createElement('audio');
    document.createElement('video');
    document.createElement('article');
    document.createElement('aside');
    document.createElement('footer');
    document.createElement('header');
    document.createElement('nav');
    document.createElement('time');
}


// override dom and some common javascript elements
base2.DOM.bind(document);
base2.JavaScript.bind(window);





