set shiftwidth=4
set expandtab
set t_ku=[A
set t_kd=[B
set t_kr=[C
set t_kl=[D

syntax on
filetype indent on
colorscheme zellner

" Jump back to last known spot in the file
au BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$") | exe "normal g'\"" | endif
