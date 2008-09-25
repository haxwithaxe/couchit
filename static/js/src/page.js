var PageUI = Class.create({
    initialize: function() {
        
        this.firstload = true;
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
            $('preview').innerHTML = self.converter.makeHtml(value);  
        }  
        this.converter_callback(this.textarea.getValue());  
        this.textarea.observe('change',self.converter_callback);
        
        this.snippet_window = new Control.Window($('snippet_window'), {
            resizable: false,
            draggable: $('snippet_window_title'),
            closeOnClick: $('snippet_window_close')
        });  
        
        this.link_window = new Control.Window($('link_window'), {
            draggable: $('link_window_title'),
            closeOnClick: $('link_window_close')
        });
        
        this.link_types_hide = {
            'url': 'page',
            'page': 'url'
        }
        
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
        
        
        window.onresize = function(e) {
            var new_height = document.viewport.getHeight() - 250;
            $('content').setStyle({'height': new_height + 'px'});
        }
        
       
        
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
                window.location.href=this.href;
            }, false);
            
        this._renamingPage = false;
        if (!Page.created && !Page.home) {
            
            this.page_title = $('page_title');
            this.page_title.setStyle({
                'cursor': 'pointer'
            });
            this.page_title.title="Click to rename";
            
            this.createRenameForm();
            //this.createRenameHelp();

            this.page_title.observe('click', function(e) {
                this._renamingPage = true;
                self.handleRename();
            }, false);
        }
            
    },
    
    init: function() {
        var active_container = this.tabs.activeContainer;  
        if (Page.created && active_container.id != "pedit")    
            this.tabs.setActiveTab("pedit");
            active_container = this.tabs.activeContainer;  
            
        if (active_container)
            this.update_tabs(active_container);
        
        /* init size of textarea */
        var new_height = document.viewport.getHeight() - 250;
        $('content').setStyle({'height': new_height + 'px'});
        
    },
    
    update_tabs: function(new_container) {
        if (new_container.id == "pedit") {
            this.Sidebar.hide();
            this.Page.setStyle({'width': '99%'});
            if (this._renamingPage) {
                this.removeRenameForm();
            }
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
              function display_link_type(selected) {
                  $('link_from_'+ selected).show();
                  $('link_from_'+self.link_types_hide[selected]).hide();
              }
              
              self.link_window.open();
              display_link_type($('link_type').getValue())
              
              $("cancelLink").observe("click", function(e) {
                  Event.stop(e);
                  self.link_window.close();
                  return false;
              });
              
              $('link_type').observe('change', function(e) {
                  var selected = this.getValue();
                  display_link_type(selected);
              }, false);
              
              var tb = this;
              var selection = this.getSelection();  
              $("slink").observe('click', function(e) {
                  Event.stop(e);
                  var link_type = $('link_type').getValue();
                  var link_text = $('link_label').getValue();
                  if (link_type == "page") {
                      tb.replaceSelection('[' + (link_text == '' ? 'Link Text' : link_text) + '](' + $('link_page').getValue() + ')');
                  } else {
                      var url = $('link_url').getValue();
;                     tb.replaceSelection('[' + (link_text == '' ? 'Link Text' : link_text) + '](' + (url == '' ? 'http://link_url/' : url).replace(/^(?!(f|ht)tps?:\/\/)/,'http://') + ')');
                  }
                  self.link_window.close();
                  return false;
              }, false);
              return
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
                    obj.replaceSelection(snippet);
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
                         obj.replaceSelection(snippet);
                         self.snippet_window.close();
                         $('snippet_content').value = "";
                      },
                      onFailure: function() {
                          alert("mmm... error while trying to fetch content from friendpaste:(")
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
            });
            
            $('snippet_url', 'snippet_language', 'snippet_content').each(function(el) {
                el.observe("focus", function(e) {
                    if (this.id == "snippet_url")
                        $('sfp').checked = true;
                    else
                        $('si').checked = true;
                }, false);
            });
  
            
          },{  
              id: 'markdown_snippet_button'  
          });

          this.toolbar.addButton('Help',function(){  
              window.open('http://daringfireball.net/projects/markdown/dingus');  
          },{  
              id: 'markdown_help_button'  
          });
    },
    
    createRenameForm: function() {
        var url_action = $('fedit').action;
        this._form = new Element('form', {
            'id': 'frename',
            'method': 'post',
            'action': url_action
        });
        var input = new Element('input', {
            'type': 'text',
            'id': 'new_title',
            'name': 'new_title',
            'maxlength': '60',
            'value': $('page_title').innerHTML
        });
        var old_title = new Element('input', {
            'type': 'hidden',
            'id': 'old_title',
            'name': 'old_title',
            'value': $('page_title').innerHTML
        });
        
        var cancel = new Element('a', {
            'id': 'rcancel',
            'class': 'cancel',
            'href':'#'
        }).update('Cancel');
        this._form.insert(old_title);
        this._form.insert(input);
        this._form.insert(cancel);
        this._form.onsubmit = this.renamePage.bind(this);
        
    },
    
    renamePage: function(e) {
        Event.stop(e);
        var new_title=$('new_title').getValue();
        var old_title=$('old_title').getValue();
        if (!new_title)
            alert("Page title can't be empty.");
        else if (old_title == new_title) {
            this.removeRenameForm();
        } else {
            new Ajax.Request(this._form.action, {
              method: 'post',
              contentType: 'application/json', 
              requestHeaders: {Accept: 'application/json'},
              postBody: Object.toJSON(this._form.serialize(true)),
              onSuccess: function(response) {
                  data = response.responseText.evalJSON(true);
                  if (data['ok']) {
                      this._renamingPage = false;
                      document.location.href = data['redirect_url'];
                  } else {
                      alert (data['error']);
                  }

              },
              onFailure: function() {
                  alert("mmm... error while trying rename :(, Please contact administrator")
              }
             });
        } 
        
    },
    
    createRenameHelp: function() {
        var self = this;
        this._help = new Element('div', {
            'class': 'rename hidden',
        }).update('&#x21E4; Click to rename');
        this.page_title.insert(this._help);
        
        this.page_title.observe('mouseover', function(e) {
            self._help.removeClassName('hidden');
        }, false);
        
        this.page_title.observe('mouseout', function(e) {
            self._help.addClassName('hidden');
        }, false);
    },
    
    removeRenameForm: function() {
        this._form.remove();
        this.createRenameForm();
        //self.createRenameHelp();
        this.page_title.show();
        this._renamingPage = false;
    },
    
    handleRename: function() {
        var self = this;
        this.page_title.hide();
        //this._help.remove();
        this.page_title.parentNode.insertBefore(this._form, $('page_title'));
        this._form.select('.cancel').each(function(el) {
            el.observe("click", function(e) {
                Event.stop(e);
                self.removeRenameForm();
                return false;
            }, false);
        });
        
        
    }
});