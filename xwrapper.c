/*
 * Copyright (C) 2014 Josef Gajdusek <atx@atx.name>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * */


#include <Python.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>

static PyObject *xwrapper_add_atom(PyObject *self, PyObject *args) {
	Window w;
	char *name;
	char *atom;

	if(!PyArg_ParseTuple(args, "kss", &w, &name, &atom))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True); /* No idea why, but nothing works without this */

	Atom prop = XInternAtom(d, name, False);
	Atom val = XInternAtom(d, atom, False);
	XChangeProperty(d, w, prop, XA_ATOM, 32, PropModeAppend, (unsigned char *) &val, 1);

	XCloseDisplay(d);

	Py_RETURN_NONE;
}

static PyObject *xwrapper_add_cardinal(PyObject *self, PyObject *args) {
	Window w;
	char *name;
	uint32_t card[1];

	if(!PyArg_ParseTuple(args, "ksk", &w, &name, &card[0]))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	Atom prop = XInternAtom(d, name, False);
	XChangeProperty(d, w, prop, XA_CARDINAL, 32, PropModeAppend, (unsigned char *) &card[0], 1);

	XCloseDisplay(d);

	Py_RETURN_NONE;
}

static PyObject *xwrapper_has_atom(PyObject *self, PyObject *args) {
	Window w;
	char *propname;
	char *atname;

	if(!PyArg_ParseTuple(args, "kss", &w, &propname, &atname))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	Atom cmp = XInternAtom(d, atname, True);
	if(!cmp) /* The Atom does not exist */
		Py_RETURN_FALSE;

	Atom type;
	int format;
	unsigned long nitems;
	unsigned long after = 1;
	Atom *data;
	Atom prop = XInternAtom(d, propname, False);
	int ret = 0;
	for(int off = 0;after;off++) {
		XGetWindowProperty(d, w, prop, off, 1, False, XA_ATOM,
							&type, &format, &nitems, &after,
							(unsigned char **) &data);

		if(type != XA_ATOM)
			break;

		if(cmp == *data) {
			ret = 1;
			break;
		}
	}

	XCloseDisplay(d);

	if(ret)
		Py_RETURN_TRUE;
	Py_RETURN_FALSE;
}

static PyObject *xwrapper_delete_property(PyObject *self, PyObject *args) {
	Window w;
	char *name;

	if(!PyArg_ParseTuple(args, "ks", &w, &name))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	Atom prop = XInternAtom(d, name, True);
	if(prop)
		XDeleteProperty(d, w, prop);

	XCloseDisplay(d);

	Py_RETURN_NONE;
}

static PyMethodDef xwrapper_methods[] = {
	{"add_atom", xwrapper_add_atom, METH_VARARGS, "Add atom to window."},
	{"add_cardinal", xwrapper_add_cardinal, METH_VARARGS, "Add cardinal to window."},
	{"has_atom", xwrapper_has_atom, METH_VARARGS, "Returns true if window does property with specified atom value."},
	{"delete_property", xwrapper_delete_property, METH_VARARGS, "Delete window property."},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef xwrapper_module = {
	PyModuleDef_HEAD_INIT,
	"xwrapper",
	NULL,
	-1,
	xwrapper_methods
};


PyMODINIT_FUNC
PyInit_xwrapper(void)
{
	return PyModule_Create(&xwrapper_module);
}
