#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include<vector>
#include<set>
#include<getopt.h>
#include <fstream>
#include <iostream>
using namespace std;
#include "ppm.h"

PPM::PPM (void)
{
    if (sizeof (ushortint) != 2)
    {
        cout << "Please redefine \"ushortint\" to be 2 bytes long\n";
        exit (0);
    }
    my_image = false;
    set_dimensions (0, 0);
    deallocate ();
}

PPM::~PPM (void)
{
    deallocate ();
}

unsigned char *
PPM::get_image (void)
{
    return image;
}

void
PPM::set_image (unsigned char *new_image)
{
    if (my_image)
    {
        delete[]image;
    }
    image = new_image;
    if (image != 0) {
        memset(image, 0, width * height * 3);
        allocated = true;
    }
    else {
        allocated = false;
    }
    my_image = false;
}

void
PPM::set_height (ushortint new_height)
{
    deallocate ();
    height = new_height;
}

void
PPM::set_width (ushortint new_width)
{
    deallocate ();
    width = new_width;
}

void
PPM::set_dimensions (ushortint new_width, ushortint new_height)
{
    set_width (new_width);
    set_height (new_height);
}

void
PPM::allocate (void)
{
    set_image (new unsigned char[width * height * 3]);
    my_image = true;
}

void
PPM::deallocate (void)
{
    set_image (0);
    allocated = false;
}

ushortint
PPM::get_width (void)
{
    return width;
}

ushortint
PPM::get_height (void)
{
    return height;
}

Dimensions
PPM::get_dimensions (void)
{
    Dimensions a;
    a.width = get_width ();
    a.height = get_height ();

    return a;
}

Pixel
PPM::get_pixel (ushortint x, ushortint y)
{
    Pixel a;
    unsigned char *spot = get_image () + ((y * width) + x) * 3;
    a.red = (*spot);
    a.green = (*(spot + 1));
    a.blue = (*(spot + 2));

    return a;
}

void
PPM::set_pixel (ushortint x, ushortint y, Pixel a)
{
    //printf("state 5\n\n");
    unsigned char *spot = get_image () + ((y * width) + x) * 3;
    //printf("state 7\nspot:%p, index:%d, x:%d, y:%d, width:%d, height:%d\n\n", spot, spot - get_image(), x, y, width, height);
    //printf("state 10\nimage:%p, get_image:%p\n\n", image, get_image());
    //printf("state 11\n%d", _msize(image));
    //printf("crash?\n%d\n\n", get_image()[((y * width) + x) * 3]);
    (*spot) = a.red;
    //printf("state 8\n\n");
    (*(spot + 1)) = a.green;
    //printf("state 9\n\n");
    (*(spot + 2)) = a.blue;
    //printf("state 6\n\n");
}


void
PPM::set_pixel (ushortint x, ushortint y, unsigned char red,
                unsigned char green, unsigned char blue)
{
    Pixel a;
    a.red = red;
    a.green = green;
    a.blue = blue;
    //printf("state 3\n\n");
    set_pixel (x, y, a);
    //printf("state 4\n\n");
}


void PPM::load_from_file(char *filename)
{
 ifstream in;
 in.open(filename, (ios::in | ios::binary));
 if (in.is_open())
 {
  load_from_stream(&in);
  in.close();
 } else
  cout << "Error loading file: " << *filename << "\n";
}

void PPM::load_from_stream(istream *in)
{
 //Dump the old image and set the dimensions to 0 in case the loading fails
 set_image(0);
 set_dimensions(0, 0);
 
 //Skip "P6" header thing
 (*in).seekg(3, ios::cur);
 char possible_hash = (*in).peek();
 if (possible_hash == '#')
 {
 	 char buf[256];
 	 //skip a line
 	 in->getline(buf,255);

 }
 ushortint new_width=0, new_height=0;
 (*in) >> new_width >> new_height;
 set_dimensions(new_width, new_height);
 
 //skip the last bit of header crap
 (*in) >> new_width;
 (*in).seekg(1, ios::cur);
 
 //Now ready to read in the binary data
 allocate();
 (*in).read((char*)get_image(), (width*height*3));
}

void PPM::save_to_file(const char *filename)
{
 ofstream out;
 out.open(filename, (ios::out | ios::binary | ios::trunc));
 if(out.is_open())
 {
  save_to_stream(&out);
  out.close();
 } else
  cout << "Error creating file: " << *filename << "\n";
}

void PPM::save_to_stream(ostream *out)
{
 //Dump the header
 (*out) << "P6\n" << get_width() << "\n" << get_height() << "\n" << 255 << "\n";
 
 //Write out the binary data
 (*out).write((char*)get_image(), (width*height*3));
}

