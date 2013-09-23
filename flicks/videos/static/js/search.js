;(function($, flicks) {
    'use strict';

    var UP = 38;
    var DOWN = 40;
    var ENTER = 13;

    $(function() {
        // Hook up the search form manipulator and autocomplete widget.
        var searchForm = new SearchForm($('.search-form'));
        new AutoComplete(searchForm);

        // Submit sorting form when the sorting input changes value.
        $('.gallery-sort select[name="sort"]').change(function() {
            $(this).parents('form').submit();
        });
    });

    /**
     * Displays an autocomplete dropdown on the search form when the user
     * enters a search query.
     */
    function AutoComplete(form) {
        this.form = form;
        this.xhr = null;
        this.lastQuery = null;
        this.autocompleteSubmit = false;

        this.bindEvents();
    }

    AutoComplete.prototype = {
        bindEvents: function() {
            var self = this;
            this.form.onQueryTyping({
                stop: function(e, $elem) {
                    self.onStopTyping(e, $elem);
                }
            });
            this.form.onQueryKeyDown(function(e) {
                self.onKeyDown(e);
            });

            // Clicking a suggestion also triggers an autocomplete search.
            this.form.onSuggestionClick(function(e) {
                self.autocompleteSubmit = true;
                self.form.setSelected(this);
                self.form.submitSelected();
            });

            // Hovering over a suggestion clears the keyboard selection.
            this.form.onSuggestionHover(function(e) {
                self.form.clearSelected();
            });

            // Clear the field input if we are not performing an autocomplete
            // search to avoid unintended field filtering.
            this.form.onSubmit(function(e) {
                if (!self.autocompleteSubmit) {
                    self.form.clearField();
                }
            });

            // If the query box loses focus, clear the selection.
            this.form.onQueryBlur(function(e) {
                self.form.clearSelected();
            });
        },

        /**
         * When the user stops typing, hide the autocomplete box and fetch new
         * suggestions, displaying the autocomplete box again if any matches
         * are found.
         */
        onStopTyping: function(e, $elem) {
            var query = this.form.getQuery();
            if (this.lastQuery && this.lastQuery === query) {
                return; // Don't bother with repeats.
            } else {
                this.lastQuery = query;
            }

            // Hide the suggestions box and abort current autocompletion.
            this.form.hideSuggestions();
            this.form.clearSelected();
            if (this.xhr) {
                this.xhr.abort();
            }

            // If empty, clear the autocomplete box but do nothing else.
            if (!query) {
                return;
            }

            // Retrieve suggestions and fill the dropdown with them.
            var self = this;
            this.xhr = $.get(this.form.autoCompleteUrl, {query: query});
            this.xhr.done(function(results) {
                var titleFound = self.form.fillSuggestion(
                    'title',
                    truncate(results.by_title, 80)
                );
                var descFound = self.form.fillSuggestion(
                    'description',
                    truncate(results.by_description, 80)
                );
                var nameFound = self.form.fillSuggestion(
                    'author',
                    truncate(results.by_author, 80)
                );

                // If at least one suggestion is found, show the dropdown.
                if (titleFound || descFound || nameFound) {
                    self.form.showSuggestions();
                }
            });
        },

        /**
         * If the user presses up or down, scroll through the available
         * suggestions. If they pressed enter and have selected one of the
         * suggestions, perform a search on that suggestion.
         */
        onKeyDown: function(e) {
            var isMoveKey = e.keyCode == UP || e.keyCode == DOWN;
            if (isMoveKey && this.form.suggestionsAreVisible()) {
                e.preventDefault();
                this.form.moveSelected(e.keyCode);
            } else if (e.keyCode == ENTER && this.form.hasSelected()) {
                this.autocompleteSubmit = true;
                this.form.submitSelected();
            }
        }
    };

    /**
     * Handles DOM manipulation of the search form for the autocomplete widget.
     */
    function SearchForm($form) {
        this.$form = $form;
        this.$query = $form.find('input[name="query"]');
        this.$field = $form.find('input[name="field"]');
        this.$suggestions = $form.find('#search-suggest');

        this.autoCompleteUrl = this.$form.data('autocompleteUrl');

        this._suggestions = {
            title: this.$suggestions.find('li[data-field="title"]'),
            description: this.$suggestions.find(
                'li[data-field="description"]'),
            author: this.$suggestions.find('li[data-field="author"]')
        };
    }

    SearchForm.prototype = {
        // Event binding.
        onQueryTyping: function(options) {
            this.$query.typing(options);
        },

        onQueryKeyDown: function(handler) {
            this.$query.keydown(handler);
        },

        onQueryBlur: function(handler) {
            this.$query.blur(handler);
        },

        onSuggestionClick: function(handler) {
            this.$suggestions.on('click', 'li:visible', handler);
        },

        onSuggestionHover: function(handler) {
            this.$suggestions.on('hover', 'li:visible', handler);
        },

        onSubmit: function(handler) {
            this.$form.submit(handler);
        },

        // Controlling the list of suggestions.

        hideSuggestions: function() {
            this.$suggestions.hide();
        },

        showSuggestions: function() {
            this.$suggestions.show();
        },

        fillSuggestion: function(field, value) {
            var $suggestion = this._suggestions[field];
            if (!$suggestion) {
                return false;
            } else if (!value) {
                $suggestion.hide();
                return false;
            } else {
                $suggestion.show().find('span').text(value);
                return true;
            }
        },

        suggestionsAreVisible: function() {
            return this.$suggestions.is(':visible');
        },

        // Manipulating the currently selected suggestion.

        clearSelected: function() {
            this.$suggestions.find('.selected').removeClass('selected');
        },

        hasSelected: function() {
            return !!this.getSelected().length;
        },

        getSelected: function() {
            return this.$suggestions.find('.selected');
        },

        moveSelected: function(direction) {
            var $current = this.getSelected();
            var $next = null;

            if (direction == UP) {
                $next = $current.prev(':visible');
                if (!$next.length) {
                    $next = this.$suggestions.find('li:visible').last();
                }
            } else {
                $next = $current.next(':visible');
                if (!$next.length) {
                    $next = this.$suggestions.find('li:visible').first();
                }
            }

            this.clearSelected();
            $next.addClass('selected');
        },

        setSelected: function(suggestion) {
            this.clearSelected();
            $(suggestion).addClass('selected');
        },

        // Miscellaneous

        clearField: function() {
            this.$field.val('');
        },

        getQuery: function() {
            return this.$query.val();
        },

        submitSelected: function() {
            var $suggestion = this.getSelected();
            if ($suggestion.length) {
                this.$query.val($suggestion.find('span').text());
                this.$field.val($suggestion.data('field'));
                this.$form.submit();
            }
        }
    };

    // Utility functions.
    function truncate(string, length, end) {
        end = end || '...';

        if (string && string.length > length) {
            string = string.substr(0, length) + end;
        }

        return string;
    }
})(jQuery, flicks);
