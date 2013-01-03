def main_redo(redo_flavour, targets):
    import vars, state, builder

    any_errors = 0

    targets = state.fix_chdir(targets)
    for t in targets:
        f = state.File(t)
        retcode = builder.build(t)
        any_errors += retcode
        if retcode and not vars.KEEP_GOING:
            return retcode
    if any_errors:
        return 1

def main_redo_ifchange(redo_flavour, targets):
    import ifchange, state, vars
    from log import debug2

    retcode = 202
    any_errors = 0

    targets = state.fix_chdir(targets)
    if vars.TARGET:
        f = state.File(name=vars.TARGET)
        debug2('TARGET: %r %r %r\n', vars.STARTDIR, vars.PWD, vars.TARGET)
    else:
        f = me = None
        debug2('redo-ifchange: no target - not adding depends.\n')

    retcode = 0
    for t in targets:
        sf = state.File(name=t)
        retcode = ifchange.build_ifchanged(sf)
        any_errors += retcode
        if f:
            sf.refresh()
            f.add_dep(sf)
        if retcode and not vars.KEEP_GOING:
            return retcode
    if any_errors:
        return 1

def main_redo_ifcreate(redo_flavour, targets):
    import os
    import vars, state
    from log import err

    targets = state.fix_chdir(targets)
    f = state.File(vars.TARGET)
    for t in targets:
        if os.path.exists(t):
            err('%s: error: %r already exists\n', redo_flavour, t)
            return 1
        else:
            f.add_dep(state.File(name=t))

def main_redo_always(redo_flavour, targets):
    import vars, state

    state.fix_chdir([])
    f = state.File(vars.TARGET)
    f.add_dep(state.File(name=state.ALWAYS))

def main_redo_stamp(redo_flavour, targets):
    import os
    import vars, state
    
    if len(targets) > 1:
        err('%s: no arguments expected.\n', redo_flavour)
        return 1

    if os.isatty(0):
        err('%s: you must provide the data to stamp on stdin\n', redo_flavour)
        return 1

    # hashlib is only available in python 2.5 or higher, but the 'sha' module
    # produces a DeprecationWarning in python 2.6 or higher.  We want to support
    # python 2.4 and above without any stupid warnings, so let's try using hashlib
    # first, and downgrade if it fails.
    try:
        import hashlib
    except ImportError:
        import sha
        sh = sha.sha()
    else:
        sh = hashlib.sha1()

    while 1:
        b = os.read(0, 4096)
        sh.update(b)
        if not b: break

    csum = sh.hexdigest()

    if not vars.TARGET:
        return 0

    state.fix_chdir([])
    f = state.File(vars.TARGET)
    f._add('%s .' % csum)

def main_redo_ood(redo_flavour, targets):
    import vars, state, deps
    from log import err

    if len(targets) != 0:
        err('%s: no arguments expected.\n', redo_flavour)
        return 1

    for f in state.files():
        if f.is_generated and f.exists():
            if deps.isdirty(f, depth='', max_runid=vars.RUNID,
                            expect_stamp=f.stamp):
                print f.name

def main_redo_sources(redo_flavour, targets):
    import state
    from log import err

    if len(targets) != 0:
        err('%s: no arguments expected.\n', redo_flavour)
        return 1

    for f in state.files():
        if f.name.startswith('//'):
            continue  # special name, ignore
        if not f.is_generated and f.exists():
            print f.name

def main_redo_targets(redo_flavour, targets):
    import state
    from log import err

    if len(targets) != 0:
        err('%s: no arguments expected.\n', redo_flavour)
        return 1

    for f in state.files():
        if f.is_generated and f.exists():
            print f.name

mains = {
    'redo-sources':  main_redo_sources,
    'redo-targets':  main_redo_targets,
    'redo-ood':      main_redo_ood,
    'redo-stamp':    main_redo_stamp,
    'redo-always':   main_redo_always,
    'redo-ifcreate': main_redo_ifcreate,
    'redo-ifchange': main_redo_ifchange,
    'redo':          main_redo}