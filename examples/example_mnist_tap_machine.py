from paysage import batch
from paysage import layers
from paysage.models import model
from paysage import fit
from paysage import optimizers
from paysage import backends as be
from paysage import schedules

be.set_seed(137) # for determinism

import example_util as util

def example_mnist_tap_machine(paysage_path=None, num_epochs=10, show_plot=False):

    num_hidden_units = 256
    batch_size = 100
    learning_rate = schedules.power_law_decay(initial=0.1, coefficient=0.1)

    (_, _, shuffled_filepath) = \
            util.default_paths(paysage_path)

    # set up the reader to get minibatches
    data = batch.HDFBatch(shuffled_filepath,
                         'train/images',
                          batch_size,
                          transform=batch.binarize_color,
                          train_fraction=0.95)

    # set up the model and initialize the parameters
    vis_layer = layers.BernoulliLayer(data.ncols)
    hid_layer = layers.BernoulliLayer(num_hidden_units)

    rbm = model.Model([vis_layer, hid_layer])
    rbm.initialize(data, 'glorot_normal')

    perf  = fit.ProgressMonitor(data,
                                metrics=['ReconstructionError',
                                         'EnergyDistance',
                                         'HeatCapacity'])

    opt = optimizers.Gradient(stepsize=learning_rate,
                              tolerance=1e-4,
                              ascent=True)

    sampler = fit.DrivenSequentialMC.from_batch(rbm, data)

    sgd = fit.SGD(rbm, data, opt, num_epochs, sampler=sampler, method=fit.tap, monitor=perf)

    # fit the model
    print('Training with stochastic gradient ascent using TAP expansion')
    sgd.train()

    util.show_metrics(rbm, perf)
    valid = data.get('validate')
    util.show_reconstructions(rbm, valid, fit, show_plot, n_recon=10, vertical=False)
    util.show_fantasy_particles(rbm, valid, fit, show_plot, n_fantasy=25)
    util.show_weights(rbm, show_plot, n_weights=25)
    # close the HDF5 store
    data.close()
    print("Done")

if __name__ == "__main__":
    example_mnist_tap_machine(show_plot = True)
