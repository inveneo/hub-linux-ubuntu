;-*-emacs-lisp-*-

(if (not (or (string= (symbol-name debian-emacs-flavor) "emacs20")
	     (string= (symbol-name debian-emacs-flavor) "emacs22")))
  (autoload 'python-mode "python-mode" "Python editing mode." t)
  (autoload 'py-shell "python-mode" "Interactive Python interpreter." t)
  (autoload 'doctest-mode "doctest-mode" "Python doctest editing mode." t)

  (setq load-path
	(append
	 (list
	  (concat "/usr/share/"
		  (symbol-name debian-emacs-flavor)
		  "/site-lisp/python-mode")
	  (concat "/usr/share/"
		  (symbol-name debian-emacs-flavor)
		  "/site-lisp/pymacs")
	  )
	 load-path))

  (setq auto-mode-alist
	(append
	 (list
	  '("\\.py$" . python-mode)
	  '("SConstruct$" . python-mode)
	  '("SConscript$" . python-mode)
	  )
	 auto-mode-alist))

  (setq interpreter-mode-alist
	(append 
	 (list
	  '("python" . python-mode) 
	  '("python2.1" . python-mode) 
	  '("python2.2" . python-mode) 
	  '("python2.3" . python-mode)
	  '("python2.4" . python-mode)
	  '("python2.5" . python-mode)
	  '("python2.6" . python-mode)
	  '("python3.0" . python-mode)
	  )
	 interpreter-mode-alist))
)
