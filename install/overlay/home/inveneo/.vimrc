set shiftwidth=4
set expandtab
syntax on
filetype indent on
colorscheme zellner

" Jump back to last known spot in the file
au BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$") | exe "normal g'\"" | endif
