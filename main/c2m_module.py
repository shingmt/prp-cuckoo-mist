import os
import numpy as np
from PIL import Image
from tensorflow.python.keras.models import load_model, Model
from utils.utils import log
# from main.data_helpers import load_data_x
from cuckoo2mist import cuckoo2mist


class Cuckoo2Mist_Module:

    _conf_dir = ''
    _apis = None
    _default_values = None


    def __init__(self, config):
        if config is None or 'conf_dir' not in config:
            log('[!][Cuckoo2Mist_Module] no `conf_dir` defined', 'warning')
            return

        log('[ ][Cuckoo2Mist_Module] config', config)
        self.change_config(config)

        log('[ ][Cuckoo2Mist_Module] self._conf_dir', self._conf_dir)
        log('[ ][Cuckoo2Mist_Module] self._apis', self._apis)

        return
    
    
    def change_config(self, config):
        if config is None:
            return

        if 'conf_dir' in config and config['conf_dir'] != self._conf_dir:
            self._conf_dir = config['conf_dir']

            if os.path.isdir(self._conf_dir):
                (self._apis, self.default_values) = cuckoo2mist.read_configuration(self._conf_dir)
            else:
                log('[!][Cuckoo2Mist_Module][change_config] `conf_dir` not exist', 'warning')

        return


    def from_files(self, _map_ohash_inputs, outdir, callback):
        print('[ ][Cuckoo2Mist_Module][from_files] _map_ohash_inputs', _map_ohash_inputs)

        if self._apis is None:
            log('[!][Cuckoo2Mist_Module][from_files] `_apis` not found', 'error')
            #? return empty result for each item
            result = {ohash: '' for ohash in _map_ohash_inputs.keys()}
            callback(result)
            return


        cuckoo2mist.generate_mist_reports(_map_ohash_inputs.items(),
                                          outputdir=outdir,
                                          apis=self._apis,
                                          default_values=self._default_values)


        #? return result
        result = {}
        note = {}
        for ohash,item in _map_ohash_inputs.items(): #? for each output corresponding to each hash
            result[ohash] = os.path.join(outdir, os.path.splitext(item)[0]+'.mist')

        #! Call __onFinishInfer__ when the analysis is done. This can be called from anywhere in your code. In case you need synchronous processing
        callback(result, note)

        return