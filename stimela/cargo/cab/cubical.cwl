cwlVersion: v1.1
class: CommandLineTool

requirements:
  EnvVarRequirement:
    envDef:
      USER: root
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.data_ms)
        writable: true
      - entryname: model_lsm
        entry: "${ return {class: 'Directory', listing: inputs.model_lsm} }"
  InplaceUpdateRequirement:
    inplaceUpdate: true

baseCommand: docker

arguments: [run, -i,
            '--volume=${var path = runtime.outdir; return path.concat("/../../");}:${var path = runtime.outdir; return path.concat("/../../");}:rw',
            --volume=$(runtime.outdir):/working_directory:rw,
            --volume=$(runtime.tmpdir):$(runtime.tmpdir),
            --workdir=/working_directory,
            --read-only=true,
            --user=2053:2053,
            '--shm-size=${var shm = "2048m";
                          var in_shm = inputs.shared_memory;
                          if (inputs.shared_memory) {
                              shm = in_shm.toString().concat("m");
                          }
                          return shm;
                         }',
            --rm, --env=TMPDIR=/tmp, --env=HOME=/working_directory, --env=USER=root,
            --cidfile=$(runtime.tmpdir)/20191115001729-761790.cid,
            stimela/cubical:devel,
            gocubical,
            --data-ms, '/working_directory/$(inputs.data_ms.basename)',
            --model-list, '${var models = "";
                             var map_order2model = {};
                             var lsms = inputs.model_lsm;
                             var columns = inputs.model_column;
                             var expressions = inputs.model_expression;
                             if (columns) {
                               for (var i in columns) {
                                 map_order2model["col_".concat(i)] = columns[i];
                               }
                             }
                             if (lsms) {
                               for (var i in lsms) {
                                 map_order2model["lsm_".concat(i)] = "/working_directory/model_lsm/".concat(lsms[i].basename);
                               }
                             }
                             for (var i in expressions) {
                               if (models) {
                                 models = models.concat(":".concat(expressions[i]));
                               } else {
                                 models = models.concat(expressions[i]);
                               }
                             }
                             for (var i in map_order2model) {
                               models = models.replace(new RegExp(i, "g"), map_order2model[i]);
                             }
                             return models;
                            }']

inputs:
  b1_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --b1-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b1_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd3_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --dd3-ref-ant
    type: string?
  misc_parset_version:
    doc: "Parset version number, for migration purposes. Can't be specified on command\n\
      line."
    inputBinding:
      prefix: --misc-parset-version
    type: string?
  sol_term_iters:
    doc: "Number of iterations per Jones term. If empty, then each Jones\nterm is\
      \ solved for once, up to convergence, or up to its -max-iter\nsetting.\nOtherwise,\
      \ set to a list giving the number of iterations per Jones term.\nFor example,\
      \ given two Jones terms and --sol-num-iter 10,20,10, it will\ndo 10 iterations\
      \ on the first term, 20 on the second, and 10 again on the\nfirst."
    inputBinding:
      prefix: --sol-term-iters
    type: string?
  out_overwrite:
    doc: Allow overwriting of existing output files. If this is set, and the output
      parset file exists, will raise an exception
    inputBinding:
      prefix: --out-overwrite
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.out_overwrite;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g3_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --g3-ref-ant
    type: string?
  g2_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --g2-prop-flags
    type: string?
  g1_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --g1-ref-ant
    type: string?
  b1_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --b1-clip-after
    type: int?
  dd2_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --dd2-max-post-error
    type: float?
  dd1_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --dd1-clip-after
    type: int?
  g_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --g-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  sol_max_bl:
    doc: Max baseline length to solve for. If 0, no maximum is applied.
    inputBinding:
      prefix: --sol-max-bl
    type: float?
  g3_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --g3-clip-high
    type: float?
  g_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --g-max-prior-error
    type: float?
  b3_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --b3-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b3_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  data_ms:
    doc: Name of measurement set (MS)
    type: Directory
  b3_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b3-time-int
    type: float?
  dd1_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd1-time-int
    type: float?
  b_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --b-fix-dirs
    type: int?
  debug_stop_before_solver:
    doc: Invoke pdb before entering the solver.
    inputBinding:
      prefix: --debug-stop-before-solver
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.debug_stop_before_solver;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g2_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --g2-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g2_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b3_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --b3-prop-flags
    type: string?
  dd2_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --dd2-load-from
    type: File?
  dd_diag_only:
    doc: If true, then data, model and gains are taken to be diagonal. Off-diagonal
      terms in data and model are ignored. This option is then enforced on all Jones
      terms.
    inputBinding:
      prefix: --dd-diag-only
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd_diag_only;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --g-load-from
    type: File?
  g3_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --g3-clip-low
    type: float?
  b2_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --b2-max-iter
    type: int?
  dist_max_chunks:
    doc: Maximum number of time/freq data-chunks to load into memory simultaneously.
      If 0, then as many as possible will be loaded.
    inputBinding:
      prefix: --dist-max-chunks
    type: int?
  g1_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g1-time-int
    type: float?
  g2_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --g2-max-prior-error
    type: float?
  b1_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --b1-max-prior-error
    type: float?
  dist_min_chunks:
    doc: "Minimum number of time/freq data-chunks to load into memory\nsimultaneously.\
      \ This number should be divisible by ncpu-1 for optimal\nperformance."
    inputBinding:
      prefix: --dist-min-chunks
    type: string?
  g2_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --g2-clip-after
    type: int?
  dd1_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --dd1-conv-quorum
    type: float?
  g2_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --g2-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g2_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  out_model_column:
    doc: If set, model visibilities will be written to the specified column.
    inputBinding:
      prefix: --out-model-column
    type: string?
  data_chunk_by:
    doc: "If set, then time chunks will be broken up whenever the value in the named\n\
      column(s) jumps by >JUMPSIZE. Multiple column names may be given, separated\n\
      by commas. Use None to disable."
    inputBinding:
      prefix: --data-chunk-by
    type: string?
  g3_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --g3-xfer-from
    type: File?
  flags_post_sol:
    doc: "If True, will do an extra round of flagging at the end  (post-solution)\n\
      \ based on solutions statistics, as per the following options."
    inputBinding:
      prefix: --flags-post-sol
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.flags_post_sol;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g1-freq-int
    type: float?
  b3_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --b3-conv-quorum
    type: float?
  g_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --g-conv-quorum
    type: float?
  data_single_chunk:
    doc: "If set, processes just one chunk of data matching the chunk ID. Useful for\n\
      debugging."
    inputBinding:
      prefix: --data-single-chunk
    type: string?
  dd_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --dd-ref-ant
    type: string?
  g1_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --g1-update-type
    type: string?
  flags_time_density:
    doc: "Minimum percentage of unflagged visibilities along the time axis required\n\
      to prevent flagging."
    inputBinding:
      prefix: --flags-time-density
    type: string?
  dd2_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd2-time-int
    type: float?
  b_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --b-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  data_time_chunk:
    doc: "Chunk data up by this number of timeslots. This limits the amount of data\n\
      processed at once. Smaller chunks allow for a smaller RAM footprint and\ngreater\
      \ parallelism, but this sets an upper limit on the solution intervals\nthat\
      \ may be employed. 0 means use full time axis."
    inputBinding:
      prefix: --data-time-chunk
    type: int?
  flags_save:
    doc: Save flags to named flagset in BITFLAG. If none or 0, will not save.
    inputBinding:
      prefix: --flags-save
    type: string?
  dist_ncpu:
    doc: Number of CPUs (processes) to use (0 or 1 disables parallelism).
    inputBinding:
      prefix: --dist-ncpu
    type: int?
  b3_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --b3-clip-after
    type: int?
  b3_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this value.
    inputBinding:
      prefix: --b3-max-post-error
    type: float?
  flags_chan_density:
    doc: "Minimum percentage of unflagged visibilities along the frequency axis\n\
      \ required to prevent flagging."
    inputBinding:
      prefix: --flags-chan-density
    type: string?
  b1_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --b1-max-iter
    type: int?
  g2_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --g2-xfer-from
    type: File?
  b1_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --b1-clip-high
    type: float?
  sol_min_bl:
    doc: Min baseline length to solve for
    inputBinding:
      prefix: --sol-min-bl
    type: float?
  b2_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b2-time-int
    type: float?
  madmax_estimate:
    doc: "MAD estimation mode. Use 'corr' for a separate estimate per each baseline\
      \ and correlation. Otherwise, a single estimate per baseline is computed using\
      \ 'all' correlations, or only the 'diag' or 'offdiag' correlations."
    inputBinding:
      prefix: --madmax-estimate
    type:
      symbols: [corr, all, diag, offdiag]
      type: enum
  dd3_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      \ enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --dd3-type
    type: string?
  b1_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --b1-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b1_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  model_beam_l_axis:
    doc: Beam l axis
    inputBinding:
      prefix: --model-beam-l-axis
    type: string?
  dd2_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      \ term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --dd2-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd2_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  montblanc_dtype:
    doc: Precision for simulation.
    inputBinding:
      prefix: --montblanc-dtype
    type: string?
  dd_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --dd-clip-high
    type: float?
  g3_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --g3-load-from
    type: File?
  g_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      \ restricts the update rule to pin the solutions within a certain subspace:\n\
      \ 'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      \ 'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --g-update-type
    type: string?
  sel_chan:
    doc: "Channels to read (within each DDID). Default reads all. Can be specified\
      \ as\ne.g. \"5\", \"10~20\" (10 to 20 inclusive), \"10:21\" (same), \"10:\"\
      \ (from 10 to\nend), \":10\" (0 to 9 inclusive), \"~9\" (same)."
    inputBinding:
      prefix: --sel-chan
    type: string?
  g1_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --g1-fix-dirs
    type: int?
  debug_pdb:
    doc: Jumps into pdb on error.
    inputBinding:
      prefix: --debug-pdb
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.debug_pdb;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd1_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      \ enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --dd1-type
    type: string?
  g3_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --g3-max-iter
    type: int?
  g2_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --g2-max-post-error
    type: float?
  model_ddes:
    doc: "Enable direction-dependent models. If 'auto', this is determined\nby --sol-jones\
      \ and --model-list, otherwise, enable/disable\nexplicitly."
    inputBinding:
      prefix: --model-ddes
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.model_ddes;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  bbc_plot:
    doc: Generate output BBC plots.
    inputBinding:
      prefix: --bbc-plot
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.bbc_plot;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --b-ref-ant
    type: string?
  b_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      \ propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --b-prop-flags
    type: string?
  b2_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --b2-fix-dirs
    type: int?
  g1_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --g1-max-iter
    type: int?
  dist_nworker:
    doc: Number of processes
    inputBinding:
      prefix: --dist-nworker
    type: int?
  b3_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      \ restricts the update rule to pin the solutions within a certain subspace:\n\
      \ 'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      \ 'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --b3-update-type
    type: string?
  g_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      \ enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --g-type
    type: string?
  g3_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --g3-fix-dirs
    type: int?
  montblanc_verbosity:
    doc: verbosity level of Montblanc's console output
    inputBinding:
      prefix: --montblanc-verbosity
    type: string?
  pin_main:
    doc: "If set, pins the main process to a separate core. If set to, pins it to the
      \ same core as the I/O process, if I/O process is pinned. Ignored if --dist-pin
      \ is not set"
    inputBinding:
      prefix: --pin-main
    type: string?
  g_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --g-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --dd-fix-dirs
    type: string?
  b2_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      \ restricts the update rule to pin the solutions within a certain subspace:\n\
      \ 'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      \ 'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --b2-update-type
    type: string?
  dd3_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --dd3-max-post-error
    type: float?
  dd_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --dd-load-from
    type: File?
  b_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b-freq-int
    type: float?
  dd1_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --dd1-fix-dirs
    type: string?
  g_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --g-max-post-error
    type: float?
  b1_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b1-freq-int
    type: float?
  dist_pin_io:
    doc: "If not 0, pins the I/O & Montblanc process to a separate core, or cores if
      \ --montblanc-threads is specified). Ignored if --dist-pin is not set"
    inputBinding:
      prefix: --dist-pin-io
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dist_pin_io;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --g1-clip-high
    type: float?
  bbc_load_from:
    doc: "Load and apply BBCs computed in a previous run. Apply with care! This will\n\
      \ tend to suppress all unmodelled flux towards the centre of the field."
    inputBinding:
      prefix: --bbc-load-from
    type: File?
  g1_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --g1-xfer-from
    type: File?
  g3_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      \ restricts the update rule to pin the solutions within a certain subspace:\n\
      \ 'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      \ 'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --g3-update-type
    type: string?
  b_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --b-conv-quorum
    type: float?
  flags_apply:
    doc: "Which flagsets will be applied prior to calibration. \nUse \"-FLAGSET\"\
      \ to apply everything except the named flagset (\"-cubical\" is\nuseful, to\
      \ ignore the flags of a previous CubiCal run)."
    inputBinding:
      prefix: --flags-apply
    type: string?
  dd2_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --dd2-conv-quorum
    type: float?
  log_verbose:
    doc: Default console output verbosity level
    inputBinding:
      prefix: --log-verbose
    type: string?
  model_beam_m_axis:
    doc: Beam m axis
    inputBinding:
      prefix: --model-beam-m-axis
    type: string?
  g1_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --g1-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g1_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd1_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --dd1-max-post-error
    type: float?
  dd1_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd1-freq-int
    type: float?
  b2_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --b2-clip-after
    type: int?
  g3_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --g3-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g3_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd2_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --dd2-clip-after
    type: int?
  g_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --g-clip-after
    type: int?
  g2_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --g2-clip-high
    type: float?
  b3_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --b3-clip-high
    type: float?
  b_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --b-type
    type: string?
  sol_delta_g:
    doc: "Theshold for gain accuracy - gains which improve by less than this value\n\
      are considered converged."
    inputBinding:
      prefix: --sol-delta-g
    type: string?
  sol_subset:
    doc: "Additional subset of data to actually solve for. Any TaQL string may be\n\
      used."
    inputBinding:
      prefix: --sol-subset
    type: string?
  dd_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --dd-prop-flags
    type: string?
  b_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --b-xfer-from
    type: File?
  sel_taql:
    doc: Additional TaQL selection string. Combined with other selection options.
    inputBinding:
      prefix: --sel-taql
    type: string?
  g_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g-time-int
    type: int?
  g1_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --g1-load-from
    type: File?
  out_column:
    doc: Output MS column name (if applicable).
    inputBinding:
      prefix: --out-column
    type: string?
  dd3_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --dd3-xfer-from
    type: File?
  b_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --b-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  log_memory:
    doc: Log memory usage.
    inputBinding:
      prefix: --log-memory
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.log_memory;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd3_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --dd3-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd3_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd1_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --dd1-clip-low
    type: float?
  dd3_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --dd3-conv-quorum
    type: float?
  dd1_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --dd1-max-iter
    type: int?
  log_file_verbose:
    doc: "Default logfile output verbosity level. \nCan either be a single number,\
      \ or a sequence of \"name=level,name=level,...\"\nassignments. If None, then\
      \ this simply follows the console level."
    inputBinding:
      prefix: --log-file-verbose
    type: string?
  b3_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b3-freq-int
    type: float?
  b3_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --b3-ref-ant
    type: string?
  g2_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --g2-clip-low
    type: float?
  dd_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd-time-int
    type: float?
  dd3_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --dd3-max-prior-error
    type: float?
  b3_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --b3-max-iter
    type: int?
  b_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --b-clip-low
    type: float?
  b_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --b-clip-after
    type: int?
  g_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g-freq-int
    type: float?
  data_column:
    doc: Name of MS column to read for data.
    inputBinding:
      prefix: --data-column
    type: string?
  montblanc_mem_budget:
    doc: Memory budget in MB for simulation.
    inputBinding:
      prefix: --montblanc-mem-budget
    type: int?
  g1_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --g1-prop-flags
    type: string?
  dd1_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --dd1-max-prior-error
    type: float?
  g_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --g-clip-high
    type: float?
  dd2_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --dd2-clip-low
    type: float?
  b_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --b-max-iter
    type: int?
  dd2_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --dd2-type
    type: string?
  out_subtract_dirs:
    doc: "Which model directions to subtract, if generating residuals. \":\"\nsubtracts\
      \ all. Can also be specified as \"N\", \"N:M\", \":N\", \"N:\", \"N,M,K\"."
    inputBinding:
      prefix: --out-subtract-dirs
    type: int?
  dd1_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --dd1-clip-high
    type: float?
  g1_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --g1-clip-after
    type: int?
  sol_jones:
    doc: "Comma-separated list of Jones terms to enable, e.g. \"G,B,dE\"\n(default:\
      \ G)"
    inputBinding:
      prefix: --sol-jones
    type: string?
  dd3_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --dd3-load-from
    type: File?
  out_mode:
    doc: "Operational mode.\n[so] solve only;\n[sc] solve and generate corrected visibilities;\n\
      [sr] solve and generate corrected residuals;\n[ss] solve and generate uncorrected\
      \ residuals;\n[ac] apply solutions, generate corrected visibilities;\n[ar] apply\
      \ solutions, generate corrected residuals;\n[as] apply solutions, generate uncorrected\
      \ residuals;"
    inputBinding:
      prefix: --out-mode
    type:
      symbols: [so, sc, sr, ss, ac, ar, as]
      type: enum
  sol_precision:
    doc: Solve in single or double precision
    inputBinding:
      prefix: --sol-precision
    type: string?
  b1_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --b1-ref-ant
    type: string?
  dd3_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --dd3-fix-dirs
    type: string?
  dd3_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --dd3-clip-after
    type: int?
  g2_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --g2-type
    type: string?
  dd1_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --dd1-ref-ant
    type: string?
  out_subtract_model:
    doc: Which model to subtract, if generating residuals.
    inputBinding:
      prefix: --out-subtract-model
    type: int?
  b2_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b2-freq-int
    type: float?
  b3_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --b3-load-from
    type: File?
  misc_random_seed:
    doc: "Seed random number generator with explicit seed. Useful for reproducibility\n\
      of the random-based optimizations (sparsification, etc.)."
    inputBinding:
      prefix: --misc-random-seed
    type: string?
  g3_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --g3-max-post-error
    type: float?
  b2_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --b2-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b2_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --g1-conv-quorum
    type: float?
  b3_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --b3-max-prior-error
    type: float?
  out_plots:
    doc: Generate summary plots.
    inputBinding:
      prefix: --out-plots
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.out_plots;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd3_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --dd3-prop-flags
    type: string?
  madmax_diag:
    doc: Flag on on-diagonal (parallel-hand) residuals
    inputBinding:
      prefix: --madmax-diag
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.madmax_diag;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --g1-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g1_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b2_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --b2-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b2_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  bbc_apply_2x2:
    doc: "Apply full 2x2 BBCs (as opposed to diagonal-only). Only enable this if you\n\
      really trust the polarisation information in your sky model."
    inputBinding:
      prefix: --bbc-apply-2x2
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.bbc_apply_2x2;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd2_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd2-freq-int
    type: float?
  g3_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --g3-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g3_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  log_append:
    doc: Append to log file if it exists.
    inputBinding:
      prefix: --log-append
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.log_append;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b1_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --b1-update-type
    type: string?
  b1_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --b1-fix-dirs
    type: int?
  madmax_plot:
    doc: Enable plots for Mad Max flagging. Use 'show' to show figures interactively.
      Plots will show the worst flagged baseline, and a median flagged baseline, provided
      the fraction of flagged visibilities is above --flags-mad-plot-thr.
    inputBinding:
      prefix: --madmax-plot
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.madmax_plot;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b3_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --b3-xfer-from
    type: File?
  sol_delta_chi:
    doc: "Theshold for solution stagnancy - if the chi-squared is improving by less\n\
      than this value, the gain is considered stalled."
    inputBinding:
      prefix: --sol-delta-chi
    type: string?
  dd2_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --dd2-clip-high
    type: float?
  b2_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --b2-ref-ant
    type: string?
  dd1_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --dd1-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd1_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b3_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --b3-type
    type: string?
  b_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --b-load-from
    type: File?
  b3_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --b3-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.b3_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b2_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --b2-max-prior-error
    type: float?
  b1_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --b1-type
    type: string?
  flags_tf_chisq_median:
    doc: "Intervals with chi-squared values larger than this value times the median\n\
      will be flagged."
    inputBinding:
      prefix: --flags-tf-chisq-median
    type: string?
  dd3_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd3-freq-int
    type: float?
  flags_auto_init:
    doc: "Insert BITFLAG column if it is missing, and initialize a named flagset\n\
      from FLAG/FLAG_ROW."
    inputBinding:
      prefix: --flags-auto-init
    type: string?
  dd2_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --dd2-max-prior-error
    type: float?
  b2_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --b2-prop-flags
    type: string?
  flags_tf_np_median:
    doc: "Minimum percentage of unflagged visibilities per time/frequncy slot\nrequired\
      \ to prevent flagging."
    inputBinding:
      prefix: --flags-tf-np-median
    type: string?
  madmax_plot_frac_above:
    doc: Threshold (in terms of fraction of visibilities flagged) above which plots
      will be generated.
    inputBinding:
      prefix: --madmax-plot-frac-above
    type: float?
  b1_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --b1-prop-flags
    type: string?
  b_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --b-clip-high
    type: float?
  dd_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --dd-xfer-from
    type: File?
  g_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --g-max-iter
    type: int?
  data_freq_chunk:
    doc: "Chunk data by this number of channels. See time-chunk for info.\n0 means\
      \ full frequency axis."
    inputBinding:
      prefix: --data-freq-chunk
    type: int?
  b2_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --b2-load-from
    type: File?
  b3_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --b3-fix-dirs
    type: int?
  montblanc_device_type:
    doc: Use CPU or GPU for simulation.
    inputBinding:
      prefix: --montblanc-device-type
    type: string?
  sel_ddid:
    doc: "DATA_DESC_IDs to read from the MS. Default reads all. Can be specified as\n\
      e.g. \"5\", \"5,6,7\", \"5~7\" (inclusive range), \"5:8\" (exclusive range),\n\
      \"5:\" (from 5 to last)."
    inputBinding:
      prefix: --sel-ddid
    type: string?
  dist_pin:
    doc: If empty or None, processes will not be pinned to cores. Otherwise, set to
      the starting core number, or 'N:K' to start with N and step by K
    inputBinding:
      prefix: --dist-pin
    type: int?
  b2_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --b2-xfer-from
    type: File?
  log_boring:
    doc: Disable progress bars and some console output.
    inputBinding:
      prefix: --log-boring
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.log_boring;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --g1-max-prior-error
    type: float?
  dd3_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --dd3-max-iter
    type: int?
  dd_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --dd-type
    type: string?
  dd1_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --dd1-xfer-from
    type: File?
  dd1_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --dd1-prop-flags
    type: string?
  flags_reinit_bitflags:
    doc: "If true, reninitializes BITFLAG column from scratch. Useful if you ended\
      \ up\nwith a dead one."
    inputBinding:
      prefix: --flags-reinit-bitflags
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.flags_reinit_bitflags;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd2_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --dd2-update-type
    type: string?
  g_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --g-fix-dirs
    type: int?
  g1_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --g1-type
    type: string?
  dist_nthread:
    doc: 'Number of OMP threads to use. 0: determine automatically.'
    inputBinding:
      prefix: --dist-nthread
    type: int?
  g_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --g-xfer-from
    type: File?
  dd2_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --dd2-prop-flags
    type: string?
  dd_dd_term:
    doc: Determines whether this term is direction dependent. --model-ddes must
    inputBinding:
      prefix: --dd-dd-term
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd_dd_term;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g3_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --g3-prop-flags
    type: string?
  b_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --b-max-post-error
    type: float?
  sel_field:
    doc: FIELD_ID to read from the MS.
    inputBinding:
      prefix: --sel-field
    type: int?
  b3_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --b3-clip-low
    type: float?
  g3_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g3-time-int
    type: float?
  dd_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --dd-max-iter
    type: int?
  g3_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --g3-clip-after
    type: int?
  dd2_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --dd2-max-iter
    type: int?
  b2_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --b2-type
    type: string?
  b1_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --b1-conv-quorum
    type: float?
  sel_diag:
    doc: If true, then data, model and gains are taken to be diagonal. Off-diagonal
      terms in data and model are ignored. This option is then enforced on all Jones
      terms.
    inputBinding:
      prefix: --sel-diag
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.sel_diag;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b2_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --b2-conv-quorum
    type: float?
  dd3_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd3-time-int
    type: float?
  sol_chi_int:
    doc: "Number of iterations to perform between chi-suqared checks. This is done\
      \ to\navoid computing the expensive chi-squared test evey iteration."
    inputBinding:
      prefix: --sol-chi-int
    type: string?
  dd_clip_after:
    doc: Number of iterations after which to clip this gain.
    inputBinding:
      prefix: --dd-clip-after
    type: int?
  weight_column:
    doc: "Column to read weights from. Weights are applied by default. Specify an\n\
      empty string to disable."
    inputBinding:
      prefix: --weight-column
    type: string?
  b1_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b1-time-int
    type: float?
  g_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --g-ref-ant
    type: string?
  montblanc_feed_type:
    doc: Simulate using linear or circular feeds.
    inputBinding:
      prefix: --montblanc-feed-type
    type: string?
  dd3_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --dd3-update-type
    type: string?
  g2_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g2-freq-int
    type: float?
  debug_panic_amplitude:
    doc: "Throw an error if a visibility amplitude in the results exceeds the given\
      \ value.\nUseful for troubleshooting."
    inputBinding:
      prefix: --debug-panic-amplitude
    type: float?
  g1_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --g1-max-post-error
    type: float?
  data_chunk_by_jump:
    doc: "The jump size used in conjunction with chunk-by. If 0, then any change in\n\
      value is a jump. If n, then the change must be >n."
    inputBinding:
      prefix: --data-chunk-by-jump
    type: float?
  dd1_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --dd1-update-type
    type: string?
  dd3_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --dd3-clip-high
    type: float?
  g2_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --g2-fix-dirs
    type: int?
  out_reinit_column:
    doc: "Reinitialize output MS column. Useful if the column is in a half-filled\n\
      or corrupt state."
    inputBinding:
      prefix: --out-reinit-column
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.out_reinit_column;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g1_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --g1-clip-low
    type: float?
  dd2_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --dd2-xfer-from
    type: File?
  dd_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --dd-conv-quorum
    type: float?
  g2_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g2-time-int
    type: float?
  madmax_threshold:
    doc: 'Threshold for MAD flagging per baseline (specified in sigmas). Residuals
      exceeding mad-thr*MAD/1.428 will be flagged. MAD is computed per baseline. This
      can be specified as a list e.g. N1,N2,N3,... The first value is used to flag
      residuals before a solution starts (use 0 to disable), the next value is used
      when the residuals are first recomputed during the solution several iteratins
      later (see -chi-int), etc. A final pass may be done at the end of the solution.
      The last value in the list is reused if necessary. Using a list with gradually
      decreasing values may be sensible. #metavar:SIGMAS'
    inputBinding:
      prefix: --madmax-threshold
      itemSeparator: ","
    type: float[]?
  madmax_global_threshold:
    doc: Threshold for global median MAD (MMAD) flagging. MMAD is computed as the
      median of the per-baseline MADs. Residuals exceeding S*MMAD/1.428 will be flagged.
      Can be specified
    inputBinding:
      prefix: --madmax-global-threshold
    type: float[]?
  dd_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --dd-max-prior-error
    type: float?
  g2_max_iter:
    doc: Maximum number of iterations spent on this term.
    inputBinding:
      prefix: --g2-max-iter
    type: int?
  b_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --b-update-type
    type: string?
  b2_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --b2-max-post-error
    type: float?
  dd_solvable:
    doc: "Set to 0 (and specify -load-from or -xfer-from) to load a non-solvable\n\
      term is loaded from disk. Not to be confused with --sol-jones, which\ndetermines\
      \ the active Jones terms."
    inputBinding:
      prefix: --dd-solvable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.dd_solvable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g2_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --g2-load-from
    type: File?
  dd_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --dd-update-type
    type: string?
  g2_update_type:
    doc: "Determines update type. This does not change the Jones solver type, but\n\
      restricts the update rule to pin the solutions within a certain subspace:\n\
      'full' is the default behaviour;\n'diag' pins the off-diagonal terms to 0;\n\
      'phase-diag' also pins the amplitudes of the diagonal terms to unity;\n'amp-diag'\
      \ also pins the phases to 0."
    inputBinding:
      prefix: --g2-update-type
    type: string?
  out_casa_gaintables:
    doc: Export gaintables to CASA caltable format. Tables are exported to same directory
      as set for cubical databases
    inputBinding:
      prefix: --out-casa-gaintables
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.out_casa_gaintables;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  dd2_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --dd2-ref-ant
    type: string?
  madmax_enable:
    doc: Enable Mad Max flagging in the solver. This computes the median absolute
      residual (i.e. median absolute deviation from zero), and flags visibilities
      exceeding the thresholds
    inputBinding:
      prefix: --madmax-enable
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.madmax_enable;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  bbc_compute_2x2:
    doc: "Compute full 2x2 BBCs (as opposed to diagonal-only). Only useful if you\n\
      really trust the polarisation information in your sky model."
    inputBinding:
      prefix: --bbc-compute-2x2
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.bbc_compute_2x2;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  g2_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --g2-conv-quorum
    type: float?
  bbc_per_chan:
    doc: Compute BBCs per-channel (else across entire band).
    inputBinding:
      prefix: --bbc-per-chan
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.bbc_per_chan;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b1_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this value."
    inputBinding:
      prefix: --b1-clip-low
    type: float?
  model_list:
    doc: Predict model visibilities from given LSM (using Montblanc).
    type: string[]?
  dd_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --dd-clip-low
    type: float?
  model_beam_pattern:
    doc: "Apply beams if specified eg. 'beam_$(corr)_$(reim).fits' or\n'beam_$(CORR)_$(REIM).fits'"
    inputBinding:
      prefix: --model-beam-pattern
    type: File?
  flags_ddid_density:
    doc: "Minimum percentage of unflagged visibilities along the DDID axis\nrequired\
      \ to prevent flagging."
    inputBinding:
      prefix: --flags-ddid-density
    type: string?
  g3_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --g3-max-prior-error
    type: float?
  b2_clip_high:
    doc: Amplitude clipping - flag solutions with any amplitudes above this value.
    inputBinding:
      prefix: --b2-clip-high
    type: float?
  g3_conv_quorum:
    doc: Minimum percentage of converged solutions to accept.
    inputBinding:
      prefix: --g3-conv-quorum
    type: float?
  g_diag_only:
    doc: if true, then data, model and gains are taken to be diagonal. off-diagonal
      terms in data and model are ignored. this option is then enforced on all jones
      terms.
    inputBinding:
      prefix: --g-diag-only
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.g_diag_only;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  sol_stall_quorum:
    doc: "Minimum percentage of solutions which must have stalled before terminating\n\
      the solver."
    inputBinding:
      prefix: --sol-stall-quorum
    type: float?
  dd_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --dd-max-post-error
    type: float?
  b2_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --b2-clip-low
    type: float?
  b_time_int:
    doc: Time solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --b-time-int
    type: float?
  dd_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --dd-freq-int
    type: float?
  b1_max_post_error:
    doc: Flag solution intervals where the posterior variance estimate is above this
      value.
    inputBinding:
      prefix: --b1-max-post-error
    type: float?
  g3_type:
    doc: "Type of Jones matrix to solve for. Note that if multiple Jones terms are\n\
      enabled, then only complex-2x2 is supported."
    inputBinding:
      prefix: --g3-type
    type: string?
  dd2_fix_dirs:
    doc: For DD terms, makes the listed directions non-solvable.
    inputBinding:
      prefix: --dd2-fix-dirs
    type: string?
  b1_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --b1-load-from
    type: File?
  g_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --g-clip-low
    type: float?
  dd1_load_from:
    doc: "Load solutions from given database. The DB must define solutions\non the\
      \ same time/frequency grid (i.e. should normally come from\ncalibrating the\
      \ same pointing/observation). By default, the Jones\nmatrix label is used to\
      \ form up parameter names, but his may be\noverridden by adding an explicit\
      \ \"//LABEL\" to the database filename."
    inputBinding:
      prefix: --dd1-load-from
    type: File?
  g2_ref_ant:
    doc: Reference antenna - its phase is guaranteed to be zero.
    inputBinding:
      prefix: --g2-ref-ant
    type: string?
  b1_xfer_from:
    doc: "Transfer solutions from given database. Similar to -load-from, but\nsolutions\
      \ will be interpolated onto the required time/frequency grid,\nso they can originate\
      \ from a different field (e.g. from a calibrator)."
    inputBinding:
      prefix: --b1-xfer-from
    type: File?
  dd3_clip_low:
    doc: "Amplitude clipping - flag solutions with diagonal amplitudes below this\n\
      value."
    inputBinding:
      prefix: --dd3-clip-low
    type: float?
  g_prop_flags:
    doc: "Flag propagation policy. Determines how flags raised on gains propagate\
      \ back\ninto the data. Options are 'never' to never propagate, 'always' to always\n\
      propagate, 'default' to only propagate flags from direction-independent gains."
    inputBinding:
      prefix: --g-prop-flags
    type: string?
  g3_freq_int:
    doc: Frequency solution interval for this term. 0 means use entire chunk.
    inputBinding:
      prefix: --g3-freq-int
    type: float?
  sol_last_rites:
    doc: "Re-estimate chi-squred and noise at the end of a solution cycle. Disabling\n\
      last rites can save a bit of time, but makes the post-solution stats less\n\
      informative."
    inputBinding:
      prefix: --sol-last-rites
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.sol_last_rites;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  madmax_offdiag:
    doc: Flag on off-diagonal (cross-hand) residuals
    inputBinding:
      prefix: --madmax-offdiag
      valueFrom: | 
        ${
          var value = 0;
          var par_value = inputs.madmax_offdiag;
          if (par_value) {
            value=1;
          }
          return value;
        }
    type: boolean?
  b_max_prior_error:
    doc: Flag solution intervals where the prior error estimate is above this value.
    inputBinding:
      prefix: --b-max-prior-error
    type: float?
  bbc_save_to:
    doc: "Compute suggested BBCs at end of run,\n\
      \ and save them to the given database.\
      \ It can be useful to have this always\n\
      \ enabled, since the BBCs provide useful diagnostics\
      \ of the solution quality\n(and are not actually\
      \ applied without a load-from setting)."
    inputBinding:
      prefix: --bbc-save-to 
    type: string
  g_save_to:
    doc: Save solutions to given database.
    inputBinding:
      prefix: --g-save-to
    type: string
  out_name:
    doc: "Base name of output files."
    inputBinding:
      prefix: --out-name
    type: string?
  model_lsm:
    doc: "List of lsm models"
    type: File[]?
  model_column:
    doc: "List of MODEL data columns"
    type: string[]?
  model_order:
    doc: "Order of the model used for calibration. .e.g. [lsm_0, lsm_1, col_0] NB: Only use either lsm_<index> or col_<index>"
    type: string[]?
  model_expression:
    doc: "Model expressions to pass to cubical. Only use either lsm_<index> or col_<index>.\
      \ This can also include dd tagged models using '@de' e.g. ['lsm_0@de+-lsm_1', 'col_0']"
    type: string[]
  shared_memory:
    doc: Memory shared between processes
    type: int?

outputs:
  parmdb_save_out:
    type: File[]
    outputBinding:
      glob: "*parmdb"
  msname_out:
    type: Directory
    outputBinding:
      outputEval: $(inputs.data_ms)
  plot_out:
    type: Directory
    outputBinding:
      glob: cubical.cc-out
  casa_plot_out:
    type: Directory[]
    outputBinding:
      glob: "*.casa"
