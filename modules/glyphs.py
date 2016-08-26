# -*- coding: utf-8 -*-


from numpy import array
from numpy import column_stack
from numpy import cos
from numpy import cumsum
from numpy import pi
from numpy import zeros
from numpy import sin
from numpy import sort
from numpy import row_stack
from numpy.random import random

from modules.helpers import _rnd_interpolate


TWOPI = 2.0*pi

def _interpolate_write_with_cursive(glyphs, inum, theta, noise, offset_size):
  stack = row_stack(glyphs)
  ig = _rnd_interpolate(stack, len(glyphs)*inum, ordered=True)

  gamma = theta + cumsum((1.0-2.0*random(len(ig)))*noise)
  dd = column_stack((cos(gamma), sin(gamma)))*offset_size
  a = ig + dd
  b = ig + dd[::-1,:]*array((1,-1))
  return a, b

def _export(self, glyphs, inum):
  stack = row_stack(glyphs)
  ig = _rnd_interpolate(stack, len(glyphs)*inum, ordered=True)
  return ig

def _get_glyph(gnum, height, width):
  from modules.helpers import random_points_in_circle
  from numpy.random import randint

  if isinstance(gnum, list):
    n = randint(*gnum)
  else:
    n = gnum

  if random()<0.2:
    shift = ((-1)**randint(0,2))*1.7
  else:
    shift = 0

  if random()<0.0:
    a = sort(TWOPI*(random()+random(n)))[::-1]
    glyph = column_stack((cos(a), shift+sin(a))) \
        *array((width, height), 'float')*0.5
  else:
    glyph = random_points_in_circle(
        n, 0, shift, 0.5
        )*array((width, height), 'float')
    _spatial_sort(glyph)

  return glyph

def _spatial_sort(glyph):
  from scipy.spatial.distance import cdist
  from numpy import argsort
  from numpy import argmin

  curr = argmin(glyph[:,0])
  visited = set([curr])
  order = [curr]

  dd = cdist(glyph, glyph)

  while len(visited)<len(glyph):
    row = dd[curr,:]

    for i in argsort(row):
      if row[i]<=0.0 or i==curr or i in visited:
        continue
      order.append(i)
      visited.add(i)
      break
  glyph[:,:] = glyph[order,:]


class Glyphs(object):
  def __init__(
      self,
      glyph_height,
      glyph_width,
      ):
    self.i = 0

    self.glyph_height = glyph_height
    self.glyph_width = glyph_width

  def write(self, position_generator, gnum, inum, cursive_noise, offset_size):
    glyphs = []

    theta = random()*TWOPI
    pg = position_generator()
    try:
      while True:
        self.i += 1
        x, y, new = next(pg)

        glyph = array((x, y), 'float') + _get_glyph(
            gnum, self.glyph_height, self.glyph_width
            )

        if not new:
          glyphs.append(glyph)
          continue

        self._current_glyph = glyphs
        yield _interpolate_write_with_cursive(
            glyphs,
            inum,
            theta,
            cursive_noise,
            offset_size
            )
        glyphs = []

    except StopIteration:
      try:
        self._current_glyph = glyphs
        yield _interpolate_write_with_cursive(
            glyphs,
            inum,
            theta,
            cursive_noise,
            offset_size
            )
      except ValueError:
        return
      except TypeError:
        return

  def export(self, position_generator, gnum, inum):
    glyphs = []

    pg = position_generator()
    try:
      while True:
        self.i += 1
        x, y, new = next(pg)

        glyph = array((x, y), 'float') + _get_glyph(
            gnum, self.glyph_height, self.glyph_width
            )

        if not new:
          glyphs.append(glyph)
          continue

        yield _export(self, glyphs, inum)
        glyphs = []

    except StopIteration:
      try:
        yield _export(self, glyphs, inum)
      except ValueError:
        return
      except TypeError:
        return

