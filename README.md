# combined_signals
Compiling GEANT
• First download the IceShelf repository here
https://github.com/sdekockere/IceShelf
The corresponding README at this link also contains detailed in-
structions to modify the ice density model and refractive index.
• Modify the ice density profile of the following script to the targeted
one (default model is South Pole):
IceDensityModels.hh
• Modify the ice refractive index profile of the following script to the
targeted one (default model is South Pole):
IceRayTracing.hh
• Modify the CMakeLists.txt file by switching these lines (l.52):
add_executable(ice_shelf ice_shelf.cpp ${sources} ${headers})
target_link_libraries(ice_shelf ${Geant4_LIBRARIES}
${ROOT_LIBRARIES} gsl)↪→
to this

• Go into the IceShelf repoository and do
mkdir build
• Eventually compile the code with
./INSTALL.sh 1

PREREQUISITES:
MARES,
CORSIKA 
