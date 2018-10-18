import sys
import numpy as np
import json
import dolfin


def main(traction, outfile='displacement.json'):

    # Create the Beam geometry
    # Length
    L = 10
    # Width
    W = 1

    print('Got traction of {} kN'.format(traction))

    # Create mesh
    mesh = dolfin.BoxMesh(dolfin.Point(0, 0, 0),
                          dolfin.Point(L, W, W),
                          30, 3, 3)

    # Mark boundary subdomians
    left = dolfin.CompiledSubDomain("near(x[0], side) && on_boundary", side=0)
    bottom = dolfin.CompiledSubDomain("near(x[2], side) && on_boundary", side=0)

    boundary_markers = dolfin.MeshFunction("size_t", mesh,
                                           mesh.topology().dim() - 1)
    boundary_markers.set_all(0)

    left_marker = 1
    bottom_marker = 2

    left.mark(boundary_markers, left_marker)
    bottom.mark(boundary_markers, bottom_marker)

    f = dolfin.File('boundary_markers.pvd')
    f << boundary_markers

    P2 = dolfin.VectorElement("Lagrange", mesh.ufl_cell(), 2)
    P1 = dolfin.FiniteElement("Lagrange", mesh.ufl_cell(), 1)
    state_space = dolfin.FunctionSpace(mesh, P2 * P1)
    state = dolfin.Function(state_space)
    state_test = dolfin.TestFunction(state_space)
    u, p = dolfin.split(state)
    v, q = dolfin.split(state_test)

    # Some mechanical quantities
    I = dolfin.Identity(3)
    gradu = dolfin.grad(u)
    F = dolfin.variable(I + gradu)
    J = dolfin.det(F)

    # Material properites
    mu = dolfin.Constant(100.0)
    lmbda = dolfin.Constant(1.0)
    epsilon = 0.5 * (gradu + gradu.T)
    # Strain energy
    W = lmbda / 2 * (dolfin.tr(epsilon)**2) \
        + mu * dolfin.tr(epsilon * epsilon)

    internal_energy = W - p * (J - 1)

    # Neumann BC
    N = dolfin.FacetNormal(mesh)
    p_bottom = dolfin.Constant(traction)
    external_work = dolfin.inner(v, p_bottom * dolfin.cofac(F) * N) \
        * dolfin.ds(bottom_marker, subdomain_data=boundary_markers)

    # Virtual work
    G = dolfin.derivative(internal_energy * dolfin.dx,
                          state, state_test) + external_work

    # Anchor the left side
    bcs = dolfin.DirichletBC(state_space.sub(0),
                             dolfin.Constant((0.0, 0.0, 0.0)), left)

    # Traction at the bottom of the beam
    dolfin.solve(G == 0, state, [bcs])

    # Get displacement and hydrostatic pressure
    u, p = state.split(deepcopy=True)

    point = np.array([10.0, 0.5, 1.0])
    disp = np.zeros(3)
    u.eval(disp, point)

    print(('Get z-position of point ({}): {:.4f} mm'
           '').format(', '.join(['{:.1f}'.format(p) for p in point]),
                      point[2] + disp[2]))

    with open(outfile, 'w') as f:
        json.dump({'point': point.tolist(),
                   'displacement': disp.tolist()}, f, indent=4)

    print('Output saved to {}'.format(outfile))

    V = dolfin.VectorFunctionSpace(mesh, "CG", 1)
    u_int = dolfin.interpolate(u, V)
    moved_mesh = dolfin.Mesh(mesh)
    dolfin.ALE.move(mesh, u_int)
    f = dolfin.File('mesh.pvd')
    f << mesh
    f = dolfin.File('bending_beam.pvd')
    f << moved_mesh


if __name__ == '__main__':

    if len(sys.argv) == 2:
        main(sys.argv[1])
    elif len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        if len(sys.argv) < 2:
            print('Not enough input argumnets')
        else:
            print('Too many input argumnets: {}'.format(sys.argv))
