set ts=4
set sw=4
set ruler
set ai
set backspace=indent,eol,start
set t_Co=256
set modeline
autocmd Filetype python setlocal et sts=4 ai omnifunc=pythoncomplete#Complete
autocmd Filetype yaml setlocal et ts=2 sw=2
:color pablo
set laststatus=2
set statusline+=%F%m%r
