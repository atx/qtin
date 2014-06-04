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

static Display *display;

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
	if(!cmp) {
		XCloseDisplay(d);
		Py_RETURN_FALSE;
	}

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

static PyObject *xwrapper_get_string(PyObject *self, PyObject *args) {
	Window w;
	char *propname;

	if(!PyArg_ParseTuple(args, "ks", &w, &propname))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	Atom prop = XInternAtom(d, propname, True);
	Atom type;
	unsigned int format;
	unsigned long nitems;
	unsigned long after;
	unsigned int *result;
	if(prop)
		XGetWindowProperty(d, w, prop, 0, 128, False, AnyPropertyType, /* 4096 chars should be enough for everything */
							&type, &format, &nitems, &after,
							(unsigned char **) &result);
	XCloseDisplay(d);

	if(!nitems || !prop)
		Py_RETURN_NONE;

	return Py_BuildValue("s", result);
}

static PyObject *xwrapper_get_cardinal(PyObject *self, PyObject *args) {
	Window w;
	char *propname;
	unsigned int offset;

	if(!PyArg_ParseTuple(args, "kks", &w, &offset, &propname))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	Atom prop = XInternAtom(d, propname, True);
	Atom type;
	unsigned int format;
	unsigned long nitems;
	unsigned long after;
	unsigned int *result;
	if(prop)
		XGetWindowProperty(d, w, prop, offset, 1, False, AnyPropertyType,
							&type, &format, &nitems, &after,
							(unsigned char **) &result);
	XCloseDisplay(d);

	if(!nitems || !prop)
		Py_RETURN_NONE;

	return Py_BuildValue("k", *result);
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

static PyObject *xwrapper_get_root_window(PyObject *self, PyObject *args) {
	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);
	Window result = DefaultRootWindow(d);
	return Py_BuildValue("k", result);
}

static PyObject *xwrapper_send_event(PyObject *self, PyObject *args) {
	XEvent xev;
	char *atname;

	if(!PyArg_ParseTuple(args, "kskkkkk", (unsigned int *) &xev.xclient.window, &atname,
							&xev.xclient.data.l[0], &xev.xclient.data.l[1],
							&xev.xclient.data.l[2], &xev.xclient.data.l[3],
							&xev.xclient.data.l[4]))
		return NULL;

	Display *d = XOpenDisplay(NULL);
	XSynchronize(d, True);

	xev.xclient.type = ClientMessage;
	xev.xclient.serial = 0;
	xev.xclient.send_event = True;
	xev.xclient.message_type = XInternAtom(d, atname, False);
	xev.xclient.format = 32;

	XSendEvent(d, DefaultRootWindow(d), True,
				SubstructureNotifyMask | SubstructureRedirectMask,
				&xev);

	XCloseDisplay(d);

	Py_RETURN_NONE;
}

static PyMethodDef xwrapper_methods[] = {
	{"add_atom", xwrapper_add_atom, METH_VARARGS, "Add atom to window."},
	{"add_cardinal", xwrapper_add_cardinal, METH_VARARGS, "Add cardinal to window."},
	{"has_atom", xwrapper_has_atom, METH_VARARGS, "Returns true if window does property with specified atom value."},
	{"get_cardinal", xwrapper_get_cardinal, METH_VARARGS, "Returns cardinal at offset."},
	{"get_string", xwrapper_get_string, METH_VARARGS, "Returns string at property."},
	{"delete_property", xwrapper_delete_property, METH_VARARGS, "Delete window property."},
	{"get_root_window", xwrapper_get_root_window, METH_VARARGS, "Returns ID of the root window."},
	{"send_event", xwrapper_send_event, METH_VARARGS, "Sends event to the WM."},
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
