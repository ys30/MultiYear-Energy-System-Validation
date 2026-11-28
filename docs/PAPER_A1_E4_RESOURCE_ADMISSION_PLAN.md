# Annual resource conversion admission plan (proposed)
## Verified inputs
Full weather QA run 45901610466: complete=true, missing_months=[], rows=10788960, admitted_cf=false.
Wind parameter run 45900246129: 850/858 exact keys, 108575.9/109341.9 MW-year snapshot sum. Curve inventory run 45905936669 queued.
## Wind
W0 generic cubic 3/12/25 m/s at 100m is an exploratory baseline.
W1 use reviewed manufacturer/model curve matches, check rated power against official MW/turbine, curve speed ordering, finite nonnegative output, normalization and cutout behavior. Preserve source hashes. Predominant model is an approximation.
W2 representative curve selected by unit rating and hub height, not observed generation fit. Keep unresolved fleet MW and fallback flags. Do not renormalize away missing capacity.
Hub-height sensitivity: v(h)=v100*(h/100)^alpha; proposed alpha 0.10, 1/7, 0.20, not measured site shear. Do not infer rated speed from EIA design wind speed.
## Solar
Existing GHI and temperature suffice for simple horizontal proxy, not full atlite ERA5 PV conversion. Candidate pvlib decomposition and transposition require verified interval semantics, solar geometry, explicit orientation, temperature and inverter assumptions. Obtain official solar tracking and DC/AC metadata before selecting primary model. No fabricated direct/diffuse observations.
## Time and validation
Confirm SSRD accumulation interval and EIA930 UTC hour-ending conventions from source documentation. Evaluate physical interval alignment before scoring. Wind instantaneous samples are not hourly mean observations. Preserve raw data and negative radiation flags. Compare annual and monthly energy bias, hourly MAE/RMSE/correlation, low-output quantiles and seasonal behavior. Earlier seasonal windows are development data, not independent holdout. Report remaining hours separately; no claim of independent future-year validation.
## Capacity experiment
Use identical within-year BA CF across S0/S1/S2 to isolate aggregate capacity effects. This holds spatial fleet composition fixed to later-year weights and is not a reconstruction of each historical fleet. Primary 42 LPs; additional 84 resource sensitivity LPs proposed, not committed. Storage and interchange admission separate.
No formal CF or annual LP admitted yet. PR #2 unmerged.
