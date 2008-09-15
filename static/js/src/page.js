var PageUI = Class.create({
    initialize: function() {
        var self = this;
        this.Sidebar = $('sidebar');
        this.Page = $('page');
        this.tabs = new Control.Tabs('tabs_wiki');
        
        this.textarea = new Control.TextArea('content');  
        this.toolbar = new Control.TextArea.ToolBar(this.textarea);  
        this.toolbar.container.id = 'markdown_toolbar';
        
        //preview of markdown text  
        this.converter = new Showdown.converter;  
        this.converter_callback = function(value){  
            $('preview').update(self.converter.makeHtml(value));  
        }  
        this.converter_callback(this.textarea.getValue());  
        this.textarea.observe('change',self.converter_callback);
        
        this.snippet_window = new Control.Window($('snippet_window'), {
            resizable: true,
            draggable: $('snippet_window_title'),
            closeOnClick: $('snippet_window_close')
        });  
        
        this.build_toolbar();
        this.init();
        
        this.tabs.observe('beforeChange', function(old_container, new_container) {
            if (!Page.created) {
                 self.update_tabs(new_container);
            } else {
                var y = window.confirm("Are you sure you want to navigate away from this page?\n\n"+
                "You have unsaved changes. Continue and discard those changes?\n\n" +
                "Click OK to continue, or click Cancel to stay on this page.");
               
                if (!y) {
                    throw $break;
                } else {
                    history.go(-1);
                }
            }
        });
        
        Event.observe(window, 'resize', function(e) {
            var new_height = document.viewport.getHeight() - 150;
            $('content').setStyle({'height': new_height + 'px'});
        });
        $('cancelEdit').observe('click', function(e) {
            Event.stop(e);
            self.tabs.setActiveTab("pview");
            return false;
        });
        
        var page_delete = $('page_delete');
        
        if (page_delete)
            page_delete.observe('click', function(e) {
                Event.stop(e);
                var y = window.confirm("Are you sure you want to delete this page?\n\n"+
                    "Click OK to continue, or click Cancel to stay on this page.");
                if (!y) {
                    return false;
                }
                document.location.href=this.href;
            }, false);
        
    },
    
    init: function() {
        var active_container = this.tabs.activeContainer;  
        if (active_container)
            this.update_tabs(active_container);
        
        /* init size of textarea */
        var new_height = document.viewport.getHeight() -150;
        $('content').setStyle({'height': new_height + 'px'});
    },
    
    update_tabs: function(new_container) {
        if (new_container.id == "pedit") {
            this.Sidebar.hide();
            this.Page.setStyle({'width': '99%'});
        } else {
            this.Page.setStyle({'width': '76%'});
            this.Sidebar.show();
        }  
    },
    
    build_toolbar: function() {
        var self = this;
         this.toolbar.addButton('Italics',function(){  
              this.wrapSelection('*','*');  
          },{  
              id: 'markdown_italics_button'  
          });  

          this.toolbar.addButton('Bold',function(){  
              this.wrapSelection('**','**');  
          },{  
              id: 'markdown_bold_button'  
          });  

          this.toolbar.addButton('Link',function(){  
              var selection = this.getSelection();  
              var response = prompt('Enter Link URL','');  
              if(response == null)  
                  return;  
              this.replaceSelection('[' + (selection == '' ? 'Link Text' : selection) + '](' + (response == '' ? 'http://link_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');  
          },{  
              id: 'markdown_link_button'  
          });  

          this.toolbar.addButton('Image',function(){  
              var selection = this.getSelection();  
              var response = prompt('Enter Image URL','');  
              if(response == null)  
                  return;  
              this.replaceSelection('![' + (selection == '' ? 'Image Alt Text' : selection) + '](' + (response == '' ? 'http://image_url/' : response).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');  
          },{  
              id: 'markdown_image_button'  
          });  

          this.toolbar.addButton('Heading',function(){  
              var selection = this.getSelection();  
              if(selection == '')  
                  selection = 'Heading';  
              this.replaceSelection("\n" + selection + "\n" + $R(0,Math.max(5,selection.length)).collect(function(){'-'}).join('') + "\n");  
          },{  
              id: 'markdown_heading_button'  
          });  

          this.toolbar.addButton('Unordered List',function(event){  
              this.collectFromEachSelectedLine(function(line){  
                  return event.shiftKey ? (line.match(/^\*{2,}/) ? line.replace(/^\*/,'') : line.replace(/^\*\s/,'')) : (line.match(/\*+\s/) ? '*' : '* ') + line;  
              });  
          },{  
              id: 'markdown_unordered_list_button'  
          });  

          this.toolbar.addButton('Ordered List',function(event){  
              var i = 0;  
              this.collectFromEachSelectedLine(function(line){  
                  if(!line.match(/^\s+$/)){  
                      ++i;  
                      return event.shiftKey ? line.replace(/^\d+\.\s/,'') : (line.match(/\d+\.\s/) ? '' : i + '. ') + line;  
                  }  
              });  
          },{  
              id: 'markdown_ordered_list_button'  
          });  

          this.toolbar.addButton('Block Quote',function(event){  
              this.collectFromEachSelectedLine(function(line){  
                  return event.shiftKey ? line.replace(/^\> /,'') : '> ' + line;  
              });  
          },{  
              id: 'markdown_quote_button'  
          });  

          this.toolbar.addButton('Code Block',function(event){  
              this.collectFromEachSelectedLine(function(line){  
                  return event.shiftKey ? line.replace(/    /,'') : '    ' + line;  
              });  
          },{  
              id: 'markdown_code_button'  
          });  
          
          this.toolbar.addButton('Snippet',function(event){  
            var selection = this.getSelection();
            if (selection) {
                // try to detect if there is a language
                var lines = selection.split('\n');
                if (lines[0].match(/\s*:::(\w*)/)) {
                    var language = lines[0].replace(/\s*:::(\w*)/, "$1");
                    lines.splice(0,1);
                    if (language) {
                        // select default language
                        $('snippet_language').select('option').each(function(el) {
                            if (el.value == language) {
                                el.selected = true;
                            }
                        });
                        
                    }
                }
                var snippet = $A(lines).collect(function(line) {
                    return line.replace(/    /,'');
                }).join('\n');
                $('snippet_content').value = snippet;
            
            }
            
            
            self.snippet_window.open();
            var obj = this;
            var insert_snippet = function(e) {
                Event.stop(e);
                var snippet_from = $('fsnippet').getInputs('radio', 'snippet_from')
                if (snippet_from[0].checked) {
                    var code = $('snippet_content').getValue();
                    code = $A(code.split("\n")).collect(function(line) {
                        line = '    ' + line;
                        return line
                    }).join('\n')
                    snippet = "\n\n    :::" + $('snippet_language').getValue() +
                    "\n" + code;
                    obj.insertAfterSelection(snippet);
                    self.snippet_window.close();
                    $('snippet_content').value = "";
                } else {
                    var url = '/proxy?url=' + encodeURIComponent($('snippet_url').getValue());
                    new Ajax.Request(url, {
                      method: 'get',
                      contentType: 'application/json', 
                      requestHeaders: {Accept: 'application/json'},
                      onSuccess: function(response) {
                          
                         data = response.responseText.evalJSON(true);
                         code = $A(data['snippet'].split('\n')).collect(function(line) {
                             return '    ' + line;
                         }).join('\n');
                         
                         snippet = " \n\n    :::" + data['language'] + "\n"  + code;
                         obj.insertAfterSelection(snippet);
                         self.snippet_window.close();
                         $('snippet_content').value = "";
                      },
                      onFailure: function() {
                          alert("fuck")
                      }
                    });
                }
                
                return false;
            }
            
            $("ssnippet").observe("click", insert_snippet, false);
            $("cancelSnippet").observe("click", function(e) {
                Event.stop(e);
                self.snippet_window.close();
                return false;
            })
          },{  
              id: 'markdown_snippet_button'  
          });

          this.toolbar.addButton('Help',function(){  
              window.open('http://daringfireball.net/projects/markdown/dingus');  
          },{  
              id: 'markdown_help_button'  
          });
    }
})