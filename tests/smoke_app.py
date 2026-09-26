import os, sys, tempfile, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ['QT_API'] = 'pyqt6'

def main():
    from PyQt6 import QtCore, QtWidgets
    temp = tempfile.TemporaryDirectory(prefix='flatcam-smoke-')
    QtCore.QSettings.setDefaultFormat(QtCore.QSettings.Format.IniFormat)
    QtCore.QSettings.setPath(QtCore.QSettings.Format.IniFormat, QtCore.QSettings.Scope.UserScope, temp.name)
    from app_Main import App
    from appGUI import VisPyPatches
    VisPyPatches.apply_patches()
    qapp = QtWidgets.QApplication([])
    app = App.__new__(App)
    status = 1
    try:
        app.__init__(qapp, user_defaults=False, data_path=Path(temp.name)/'data', single_instance=os.environ.get('FLATCAM_SMOKE_SINGLE_INSTANCE') == '1')
        print('STARTUP_OK', flush=True)
        app.inform.connect(lambda msg: print('INFORM:', msg, flush=True))
        app.f_handlers.open_gerber(str(ROOT/'assets/examples/files/test.gbr'), outname='smoke_gerber')
        app.f_handlers.open_excellon(str(ROOT/'assets/examples/files/test.txt'), outname='smoke_drill')
        qapp.processEvents()
        print('OBJECTS:', app.collection.get_names(), flush=True)
        assert app.collection.get_by_name('smoke_gerber') is not None
        assert app.collection.get_by_name('smoke_drill') is not None
        gerber = app.collection.get_by_name('smoke_gerber')
        print('GERBER_BOUNDS', gerber.bounds(), flush=True)
        gerber.isolate(dia=0.2, passes=1, combine=True, outname='smoke_iso', plot=True)
        qapp.processEvents()
        geo = app.collection.get_by_name('smoke_iso')
        assert geo is not None
        print('ISOLATE_OK', flush=True)
        geo.generatecncjob(outname='smoke_cnc', dia=0.2, z_cut=-0.1, z_move=2.0, feedrate=120, use_thread=False)
        qapp.processEvents()
        cnc = app.collection.get_by_name('smoke_cnc')
        assert cnc is not None
        assert cnc.gcode and cnc.gcode_parsed
        print('CNC_OK', len(cnc.gcode), flush=True)
        project = str(Path(temp.name)/'smoke.FlatPrj')
        app.f_handlers.save_project(project, silent=True)
        assert Path(project).stat().st_size > 0
        app.should_we_save = False
        app.f_handlers.open_project(project, plot=True)
        qapp.processEvents()
        assert set(app.collection.get_names()) == {'smoke_gerber', 'smoke_drill', 'smoke_iso', 'smoke_cnc'}
        assert app.collection.get_by_name('smoke_cnc').gcode == cnc.gcode
        print('PROJECT_ROUNDTRIP_OK', flush=True)
        app.collection.set_active('smoke_gerber')
        app.ui.splitter.setSizes([300, 700])
        app.on_zoom_fit()
        app.should_we_save = False
        def finish():
            app.ui.grab().save(str(ROOT/'.venv/startup-smoke.png'))
            print('RENDER_OK', flush=True)
            qapp.quit()
        QtCore.QTimer.singleShot(2500, finish)
        qapp.exec()
        status = 0
    except BaseException:
        traceback.print_exc()
    finally:
        if hasattr(app, 'pool'):
            app.pool.terminate()
            app.pool.join()
        if hasattr(app, 'workers'):
            for thread in app.workers.threads:
                thread.quit()
                thread.wait(2000)
        sys.stdout.flush()
        sys.stderr.flush()
    return status

if __name__ == '__main__':
    sys.exit(main())
