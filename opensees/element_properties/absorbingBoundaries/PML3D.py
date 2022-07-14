import PyMpc.Units as u
from PyMpc import *
from mpc_utils_html import *
import importlib
import opensees.utils.tcl_input as tclin
import math
import os

def makeXObjectMetaData():
	
	dp = 'https://www.sciencedirect.com/science/article/abs/pii/S0266352X19302071'
	def mka(name, type, description, group, dimension = None, default = None):
		a = MpcAttributeMetaData()
		a.type = type
		a.name = name
		a.group = group
		a.description = (
			html_par(html_begin()) +
			html_par(html_boldtext(name)+'<br/>') + 
			html_par(description) +
			html_par(html_href(dp,'PML3D')+'<br/>') +
			html_end()
			)
		if dimension:
			a.dimension = dimension
		if default:
			a.setDefault(default)
		return a
	
	E = mka('E', MpcAttributeType.QuantityScalar, "Young's modulus", 'Material parameters', dimension=u.F/u.L**2)
	v = mka('v', MpcAttributeType.Real, "Poisson's ratio", 'Material parameters')
	rho = mka('rho', MpcAttributeType.Real, 'Mass Density', 'Material parameters')
	
	th = mka('thickness', MpcAttributeType.QuantityScalar, 'Thickness of the PML domain', 'Geometry', dimension=u.L)
	HLX = mka('HLX', MpcAttributeType.QuantityScalar, 'Halfwidth of the interior domain in x-direction', 'Geometry', dimension=u.L)
	HLY = mka('HLY', MpcAttributeType.QuantityScalar, 'Halfwidth of the interior domain in y-direction', 'Geometry', dimension=u.L)
	LZ = mka('LZ', MpcAttributeType.QuantityScalar, 'Depth of the interior domain in z-direction', 'Geometry', dimension=u.L)
	
	m = mka('m', MpcAttributeType.Real, 'M Coefficient', 'Misc', default=2.0)
	R = mka('R', MpcAttributeType.Real, 'R Coefficient', 'Misc', default=1.0e-8)
	
	alpha = mka('alpha', MpcAttributeType.Real, 'Damping alpha coefficient', 'Damping')
	beta = mka('beta', MpcAttributeType.Real, 'Damping beta coefficient', 'Damping')
	
	
	xom = MpcXObjectMetaData()
	xom.name = 'PML3D'
	
	xom.addAttribute(E)
	xom.addAttribute(v)
	xom.addAttribute(rho)
	
	xom.addAttribute(th)
	xom.addAttribute(HLX)
	xom.addAttribute(HLY)
	xom.addAttribute(LZ)
	
	xom.addAttribute(m)
	xom.addAttribute(R)
	
	xom.addAttribute(alpha)
	xom.addAttribute(beta)
	
	return xom

def _geta(xobj, name):
	at = xobj.getAttribute(name)
	if(at is None):
		raise Exception('Error: cannot find "{}" attribute'.format(name))
	return at

def getNodalSpatialDim(xobj, xobj_phys_prop):
	return [(3,18),(3,18),(3,18),(3,18),(3,18),(3,18),(3,18),(3,18)]	#(ndm, ndf)

def writeTcl(pinfo):
	
	# element PML3D eleTag? [8 integer nodeTags] [PML3D_NUM_PARAMS material properties]
	
	# standardized error
	def err(msg):
		return 'Error in "PML3D" :\n{}'.format(msg)
	
	elem = pinfo.elem
	elem_prop = pinfo.elem_prop
	
	tag = elem.id
	xobj = elem_prop.XObject
	
	# info
	ClassName = xobj.name
	if pinfo.currentDescription != ClassName:
		pinfo.out_file.write('\n{}# {} {}\n'.format(pinfo.indent, xobj.Xnamespace, ClassName))
		pinfo.currentDescription = ClassName
	
	# get parameters
	E = _geta(xobj, 'E').quantityScalar.value
	v = _geta(xobj, 'v').real
	rho = _geta(xobj, 'rho').real
	th = _geta(xobj, 'thickness').quantityScalar.value
	HLX = _geta(xobj, 'HLX').quantityScalar.value
	HLY = _geta(xobj, 'HLY').quantityScalar.value
	LZ = _geta(xobj, 'LZ').quantityScalar.value
	m = _geta(xobj, 'm').real
	R = _geta(xobj, 'R').real
	alpha = _geta(xobj, 'alpha').real
	beta = _geta(xobj, 'beta').real
	
	# check element type
	if (elem.geometryFamilyType()) != MpcElementGeometryFamilyType.Hexahedron or len(elem.nodes)!=8:
		raise Exception(err('invalid type of element or number of nodes, It should be a Hexahedron with 8 nodes, not a {} with {} nodes'
			.format(elem.geometryFamilyType(), len(elem.nodes))))
	
	# get connectivity
	N1 = [elem.nodes[i].id for i in range(8)]
	
	# now write the string into the file
	pinfo.out_file.write(
		'{}element PML {}   {} {} {} {} {} {} {} {}   {} {} {}   {}   {} {} {}   {} {} {}   {} {}\n'.format(
			pinfo.indent, tag, *N1, 
			E, v, rho, 6, th, m, R, HLX, HLY, LZ, alpha, beta)
		)