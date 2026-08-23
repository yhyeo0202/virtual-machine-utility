#!/bin/bash

if ! grep -q "Customized theme" /etc/vim/vimrc; then
	cat <<  'EOF' >> /etc/vim/vimrc
" Customized theme
colorscheme desert
set number
set title

set autoindent
set linebreak
set breakindent
set tabstop=4
set shiftwidth=4

set whichwrap+=<,>,[,]

set scrolloff=5
set display+=lastline

set hlsearch
set ignorecase

set history=1000

set signcolumn=yes
set updatetime=1000

inoremap " ""<left>
inoremap ' ''<left>
inoremap ( ()<left>
inoremap [ []<left>
inoremap { {}<left>
inoremap < <><left>
inoremap {<CR> {<CR>}<ESC>O
inoremap {;<CR> {<CR>};<ESC>O

noremap <silent> k gk
noremap <silent> j gj
noremap <silent> 0 g0
noremap <silent> $ g$
noremap <silent> <Up> g<Up>
noremap <silent> <Down> g<Down>
EOF
fi
