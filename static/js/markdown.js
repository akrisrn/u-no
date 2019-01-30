(function () {
    'use strict';

    /**
     * Targets special code or div blocks and converts them to UML.
     * @param {object} converter is the object that transforms the text to UML.
     * @param {string} className is the name of the class to target.
     * @param {object} settings is the settings for converter.
     * @return {void}
     */
    const uml = (function (converter, className, settings) {
        const getFromCode = function getFromCode(parent) {
            // Handles <pre><code>
            let text = "";
            for (let j = 0; j < parent.childNodes.length; j++) {
                const subEl = parent.childNodes[j];
                if (subEl.tagName.toLowerCase() === "code") {
                    for (let k = 0; k < subEl.childNodes.length; k++) {
                        const child = subEl.childNodes[k];
                        const whitespace = /^\s*$/;
                        if (child.nodeName === "#text" && !whitespace.test(child.nodeValue)) {
                            text = child.nodeValue;
                            break;
                        }
                    }
                }
            }
            return text;
        };

        const getFromDiv = function getFromDiv(parent) {
            // Handles <div>
            return parent.textContent || parent.innerText;
        };

        // Change body to whatever element your main Markdown content lives.
        const body = document.querySelectorAll("body");
        const blocks = document.querySelectorAll("pre." + className + ",div." + className
            // Is there a settings object?
        );
        const config = settings === void 0 ? {} : settings;

        // Find the UML source element and get the text
        for (let i = 0; i < blocks.length; i++) {
            const parentEl = blocks[i];
            const el = document.createElement("div");
            el.className = className;
            el.style.visibility = "hidden";
            el.style.position = "absolute";

            const text = parentEl.tagName.toLowerCase() === "pre" ? getFromCode(parentEl) : getFromDiv(parentEl);

            // Insert our new div at the end of our content to get general
            // typeset and page sizes as our parent might be `display:none`
            // keeping us from getting the right sizes for our SVG.
            // Our new div will be hidden via "visibility" and take no space
            // via `position: absolute`. When we are all done, use the
            // original node as a reference to insert our SVG back
            // into the proper place, and then make our SVG visible again.
            // Lastly, clean up the old node.
            body[0].appendChild(el);
            const diagram = converter.parse(text);
            diagram.drawSVG(el, config);
            el.style.visibility = "visible";
            el.style.position = "static";
            parentEl.parentNode.insertBefore(el, parentEl);
            parentEl.parentNode.removeChild(parentEl);
        }
    });

    (function () {
        const onReady = function onReady(fn) {
            if (document.addEventListener) {
                document.addEventListener("DOMContentLoaded", fn);
            } else {
                document.attachEvent("onreadystatechange", function () {
                    if (document.readyState === "interactive") {
                        fn();
                    }
                });
            }
        };

        onReady(function () {
            if (typeof flowchart !== "undefined") {
                uml(flowchart, "uml-flowchart");
            }

            if (typeof Diagram !== "undefined") {
                uml(Diagram, "uml-sequence-diagram", {theme: "simple"});
            }
        });
    })();
}());

$(function () {
    $("#content").find("table").tablesorter({sortList: [[0, 0]]});

    $('.star').raty({
        readOnly: true,
        starType: "i"
    });

    $("ul>li:first-child>details, ol>li:first-child>details").each(function () {
        this.innerHTML = this.innerHTML.replace(/<\/summary>\s/, "</summary><p>") + "</p>"
    });

    const toc = $(".toc");
    if (toc.length > 0) {
        let tocDetails = $("<details>");
        tocDetails.addClass("toc");
        if (toc.find("ul>li").length === 0) {
            tocDetails.css("display", "none");
        }
        toc.wrap(tocDetails);
        const tocDetailsSummary = $("<summary>");
        tocDetailsSummary.append($("<strong>").text("TOC"));
        tocDetailsSummary.insertBefore(toc);
        $(toc.find('ul').get().reverse()).each(function () {
            $(this).replaceWith($('<ol class="number" style="margin-bottom: 8px">' + $(this).html() + '</ol>'))
        });
        const changeTop = (tocDetails, scrollTop) => {
            const markdownBody = $(".markdown-body");
            const headerHeight = markdownBody.offset().top - 16;
            const bodyHeight = markdownBody.height() + markdownBody.offset().top;
            const isFixed = tocDetails.css("position") === "fixed";
            if (scrollTop + tocDetails.height() + 16 > bodyHeight) {
                tocDetails.css("top", isFixed ? bodyHeight - tocDetails.height() - 16 - scrollTop :
                    bodyHeight - tocDetails.height() - 16)
            } else {
                tocDetails.css("top", scrollTop > headerHeight ? (isFixed ? 0 : scrollTop) :
                    (isFixed ? headerHeight - scrollTop : headerHeight));
            }
        };
        const changeSth = (tocDetails) => {
            tocDetails.css("max-height", window.innerHeight - 50);
            if (window.innerWidth > 1380) {
                tocDetails.attr("open", "")
            } else {
                tocDetails.removeAttr("open")
            }
        };
        setTimeout(() => {
            tocDetails = $("details.toc");
            tocDetails.appendTo($(".markdown-body"));
            changeSth(tocDetails);
            changeTop(tocDetails, getScrollTop());
        }, 1);
        $(window).resize(() => {
            const tocDetails = $("details.toc");
            changeSth(tocDetails);
            changeTop(tocDetails, getScrollTop());
        });
        $(window).scroll(() => {
            changeTop($("details.toc"), getScrollTop());
        });
    }

    $("summary").each(function () {
        if (this.innerHTML === "") {
            this.style.display = "none"
        }
    });

    $("p>script").each(function () {
        $(this).unwrap("p")
    });

    $(".markdown-body").find("h1,h2,h3,h4,h5.h6").each(function () {
        $(this).wrap($("<a style='color: #24292e'>").attr("href", "#" + $(this).attr("id")));
    });
});